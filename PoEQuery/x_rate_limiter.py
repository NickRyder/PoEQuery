import asyncio
import logging
import time
from asyncio import Lock
from asyncio.events import AbstractEventLoop
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List

import requests
from requests.models import Response


@dataclass
class XRate:
    request_count: int
    time_frame: int
    timeout: int

    def __init__(self, xrate: str):
        self.request_count, self.time_frame, self.timeout = [
            int(x) for x in xrate.split(":")
        ]


@dataclass
class XRateLimitState:
    limit: XRate
    state: XRate


@dataclass
class XRateLimitStates:
    rule: str
    limit_states: List[XRateLimitState]


@dataclass
class XRateResponse:
    date: datetime
    policy: str
    rules: List[str]
    named_limit_states: List[XRateLimitStates]

    def __init__(self, response: Response):

        self.rules = response.headers["X-Rate-Limit-Rules"].split(",")
        self.policy = response.headers["X-Rate-Limit-Policy"]

        self.named_limit_states = []

        for rule in self.rules:
            limits = response.headers[f"X-Rate-Limit-{rule}"].split(",")
            states = response.headers[f"X-Rate-Limit-{rule}-State"].split(",")
            limit_states = []
            for limit, state in zip(limits, states):
                limit_states.append(
                    XRateLimitState(limit=XRate(limit), state=XRate(state))
                )

            self.named_limit_states.append(
                XRateLimitStates(rule=rule, limit_states=limit_states)
            )

        self.date = datetime.strptime(
            response.headers["Date"], "%a, %d %b %Y %H:%M:%S %Z"
        )


# Global objects which keep track of the wait time needed for the x_rate_policy
# The lock should be used for accessing, waiting, and modifying the wait time
# Asyncio gets mad if you create a lock in a different loop, so i need to enumerate
# the locks by loop.
# This will not work with multithreading/processsing
locks_by_policy: Dict[AbstractEventLoop, Dict[str, Lock]] = defaultdict(
    lambda: defaultdict(Lock)
)
wait_times_by_policy: Dict[str, int] = defaultdict(int)


def rate_limited(x_rate_policy):
    def rate_limited_decorator(
        function: Callable[..., requests.Response]
    ) -> Callable[..., requests.Response]:
        async def rate_limited_function(*args, **kwargs):
            request_lock = locks_by_policy[asyncio.get_running_loop()][x_rate_policy]
            async with request_lock:
                request_wait_time = wait_times_by_policy[x_rate_policy]
                if request_wait_time is not None:
                    wait_time = max(0, request_wait_time - time.monotonic())
                    await asyncio.sleep(wait_time)

                response = function(*args, **kwargs)

                if not isinstance(response, requests.Response):
                    raise TypeError(
                        f"the functions wrapped must output requests.Response instead of {type(response)}"
                    )

                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    logging.warning(e)

                x_rate_response = XRateResponse(response)
                assert (
                    x_rate_response.policy == x_rate_policy
                ), f"""x_rate_policy ({x_rate_policy}) didnt match response ({x_rate_response.policy})
                       try updating the decorator policy to be {x_rate_response.policy}"""

                wait_time = time_to_wait_on_new_response(x_rate_response)
                wait_times_by_policy[x_rate_policy] = time.monotonic() + wait_time
                return response

        return rate_limited_function

    return rate_limited_decorator


class ResponseSortedQueue:
    """
    a private queue which keeps the XRateResponses in date order
    """

    def __init__(self):
        self._deque = deque()

    def append_and_cull(self, response_to_append: XRateResponse, max_time_frame: int):
        """
        ensures things are kept sorted, takes in a max_time_frame int which will
        popleft all responses which are out of the time frame
        """
        assert (
            len(self._deque) == 0 or self._deque[-1].date <= response_to_append.date
        ), f"responses must be added in order {self._deque[-1].date, response_to_append.date}"
        self._deque.append(response_to_append)

        while (
            response_to_append.date - self._deque[0].date
        ).total_seconds() > max_time_frame:
            self._deque.popleft()

    def sorted_response_times_within_range(
        self, target_response: XRateResponse, time_frame: int
    ) -> List[int]:
        """
        returns sorted list of all times from target_response to responses
        in the queue which are within time_frame
        """

        response_times = [
            (target_response.date - response.date).total_seconds()
            for response in self._deque
            if (target_response.date - response.date).total_seconds() <= time_frame
        ]
        return response_times[::-1]


recent_x_rate_responses: Dict[str, ResponseSortedQueue] = defaultdict(
    ResponseSortedQueue
)


def time_to_wait_on_new_response(x_rate_response: XRateResponse) -> int:
    """
    response: a requests.model.Response object from a request which contains the following keys in its header:
    X-Rate-Limit-Policy
    X-Rate-Limit-Rules
    X-Rate-Limit-###
    X-Rate-Limit-###-State
    Date

    returns:
    the number of seconds one should wait before sending another request to this endpoint
    """

    time_frames = [
        limit_state.limit.time_frame
        for named_limit_state in x_rate_response.named_limit_states
        for limit_state in named_limit_state.limit_states
    ]
    max_time_frame = max(time_frames)
    recent_x_rate_responses[x_rate_response.policy].append_and_cull(
        x_rate_response, max_time_frame
    )

    wait_times: List[int] = []
    for named_limit_state in x_rate_response.named_limit_states:
        for limit_state in named_limit_state.limit_states:
            if limit_state.state.timeout > 0:
                logging.warn(f"pre-existing timeout: {limit_state.state.timeout}")
                wait_times.append(limit_state.state.timeout)
            elif limit_state.state.request_count == limit_state.limit.request_count:
                response_times = recent_x_rate_responses[
                    x_rate_response.policy
                ].sorted_response_times_within_range(
                    x_rate_response, limit_state.state.time_frame
                )

                if len(response_times) < limit_state.state.request_count:
                    logging.warn(
                        f"could not find adequate number of recent requests\
                         {len(response_times)}/{limit_state.state.request_count},\
                              defaulting to waiting out time_frame for oldest request,\
                                   {limit_state.state.time_frame - response_times[-1]}"
                    )
                    wait_times.append(limit_state.state.time_frame - response_times[-1])
                else:
                    wait_times.append(
                        limit_state.limit.time_frame
                        - response_times[limit_state.state.request_count - 1]
                    )

    return max(wait_times) if wait_times else 0
