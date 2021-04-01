from typing import Dict, List
from requests.models import Response
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime
import logging


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
    name: str
    limit_states: List[XRateLimitState]


@dataclass
class XRateResponse:
    date: datetime
    policy: str
    named_limit_states: List[XRateLimitStates]

    def __init__(self, response: Response):

        state_names = [
            k
            for k in response.headers.keys()
            if k.startswith("X-Rate") and k.endswith("-State")
        ]

        x_rate_limit_states = []

        for state_name in state_names:
            # e.g. X-Rate-Limit-Account-Ip
            state_name_words = state_name.split("-")
            # e.g. X-Rate-Limit-Account
            limit_name = "-".join(state_name_words[:-1])
            # e.g. Account
            name = "-".join(state_name_words[3:-1])
            limits = response.headers[limit_name]
            states = response.headers[state_name]
            limit_states = []
            for limit, state in zip(limits.split(","), states.split(",")):
                limit_states.append(
                    XRateLimitState(limit=XRate(limit), state=XRate(state))
                )

            x_rate_limit_states.append(
                XRateLimitStates(name=name, limit_states=limit_states)
            )

        self.date = datetime.strptime(
            response.headers["Date"], "%a, %d %b %Y %H:%M:%S %Z"
        )
        self.policy = response.headers["X-Rate-Limit-Policy"]
        self.named_limit_states = x_rate_limit_states


recent_x_rate_responses: Dict[str, List[XRateResponse]] = defaultdict(list)


def time_to_wait_on_new_response(response: Response, x_rate_policy: str):
    """
    response: a requests.model.Response object from a request which contains the following keys:
    X-Rate-Limit-Policy
    X-Rate-Limit-###
    X-Rate-Limit-###-State
    Date

    returns:
    the number of seconds one should wait before sending another request to this endpoint
    """
    x_rate_response = XRateResponse(response)
    assert (
        x_rate_response.policy == x_rate_policy
    ), f"x_rate_policy ({x_rate_policy}) didnt match response ({x_rate_response.policy})"
    recent_x_rate_responses[x_rate_response.policy].append(x_rate_response)

    # filter out old responses
    time_frames = [
        limit_state.limit.time_frame
        for named_limit_state in x_rate_response.named_limit_states
        for limit_state in named_limit_state.limit_states
    ]
    max_time_frame = max(time_frames)
    recent_x_rate_responses[x_rate_response.policy] = [
        response
        for response in recent_x_rate_responses[x_rate_response.policy]
        if (x_rate_response.date - response.date).total_seconds() <= max_time_frame
    ]

    wait_times = []
    for named_limit_state in x_rate_response.named_limit_states:
        for limit_state in named_limit_state.limit_states:
            if limit_state.state.timeout > 0:
                logging.warn(f"pre-existing timeout: {limit_state.state.timeout}")
                wait_times.append(
                    limit_state.state.timeout
                )  # already timedout, we should wait
            elif limit_state.state.request_count == limit_state.limit.request_count:
                responses_from_time_frame = [
                    response
                    for response in recent_x_rate_responses[x_rate_response.policy]
                    if (x_rate_response.date - response.date).total_seconds()
                    <= limit_state.state.time_frame
                ]
                response_times = sorted(
                    [
                        (x_rate_response.date - response.date).total_seconds()
                        for response in responses_from_time_frame
                    ]
                )
                if len(responses_from_time_frame) < limit_state.state.request_count:
                    logging.warn(
                        f"could not find adequate number of recent requests {len(responses_from_time_frame)}/{limit_state.state.request_count}, defaulting to waiting out time_frame for oldest request, {limit_state.state.time_frame - response_times[-1]}"
                    )
                    wait_times.append(limit_state.state.time_frame - response_times[-1])
                else:
                    wait_times.append(
                        limit_state.limit.time_frame
                        - response_times[limit_state.state.request_count - 1]
                    )

    return max(wait_times) if wait_times else 0
