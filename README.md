# task-api
### Golem - application communication interface
This work is in it's alpha stage and under heavy development so the interface may change frequently.

This repository contains the interface that the Golem compatible application should implement as well as constants used by the protocol. The interface and the constants are defined under the `proto` directory in the [Protocol Buffers](https://developers.google.com/protocol-buffers/) files.

This repository also contains programming language specific packages of the `gRPC` protocol which may be used for concrete implementation. This is for the ease of development of the application but it's not required to use them in the application.
If you don't see a programming language you're interested in, feel free to create an issue or even a pull request and we will add it.

# The API
The application is a service that listens on a certain set of RPC events.

It receives a single working directory (let's call it `work_dir`) when it's spawned and serves the following methods:
- requestor side
  - `CreateTask`
    - takes two arguments `task_id` and `task_params_json`
    - can assume that the following directories exist under `work_dir`
      - `task_id`
      - `task_id/constants.RESOURCES`
      - `task_id/constants.NETWORK_RESOURCES`
      - `task_id/constants.RESULTS`
      - `task_id/constants.NETWORK_RESULTS`
    - should treat `work_dir/task_id` as the working directory for the given task
    - `task_params_json` is a JSON string containing task specific parameters
    - will only be called once with given `task_id`
    - can assume `task_id/constants.RESOURCES` contains all the resources provided by task creator
  - `NextSubtask`
    - takes one argument `task_id`
    - can assume `CreateTask` was called earlier with the same `task_id`
    - returns `subtask_id` which can be an arbitrary string but the same string cannot be returned more than once
    - also returns `subtask_params_json` which is the JSON string containing subtask specific parameters
  - `Verify`
    - takes two arguments `task_id` and `subtask_id` which specify which subtask results should be verified
    - will be called with only valid `task_id` and `subtask_id` values
    - returns a boolean indicating whether results passed the verification or not
    - for successfully verified subtasks it most likely should also perform merging the partial results into the final one
- provider side
  - `Compute`
    - takes `task_id`, `subtask_id`, `subtask_params_json`
    - can assume the following directoees exist under `work_dir`
      - `task_id`
      - `task_id/constants.NETWORK_RESOURCES`
    - can assume that under `task_id/constants.NETWORK_RESOURCES` are the resources specified corresponding `NextSubtask` call
    - generates a single `result.zip` file under `work_dir/task_id` (subject likely to change) which is the result that will be sent back to the requestor
- both sides
  - `Benchmark`
    - takes no arguments
    - reteurns a score which indicates how efficient the machine is for this type of tasks
    - shouldn't take much time (preferably less than a minute for medium range machines)


When the last subtask is successfully verified on the requestor's side, the `work_dir/task_id/constants.RESULTS` directory should contain all result files and nothing else.
