# Deployment Director

Plug this utility in your CI/CD pipeline and customise your deployment flow
with advanced logic using simple yaml configuration.

Docker support required.

## How to run

```
Usage: deployment-director [OPTIONS] RULES_FILE

Options:
  --ci-name TEXT      Name of the CI product deployment director is running
                      under
  -n, --dry-run TEXT  Do not actually execute any actions, just print them out
  -v, --verbose
  --help              Show this message and exit.
```

## The rules file

Sample:

```
version: "1"
rules:
  - when:
    - branch: [ master, development ]
    then:
    - add_action:
        name: deploy
        action:
          class_name: CommandAction
          arguments:
            command: deploy.sh {server_ip}
        parameters:
          server_ip:
            key: branch
            map:
              master: 10.0.0.1
              development: 10.0.1.1
```

A decomposition follows:

### Version

Version of the file, we just have version 1 (string) so far

    version: "1"

### Rules

The bulk of the file is a list of rules. Each rule has a `when` and a `then`
clause:

```
rules:
  - when: ...
    then: ...
  - when: ...
    then: ...
```

Rules are evaluated sequentially.

### Rule conditions

Conditions belong to the `when` clause of the rules. They indicate when the
rule consequences (`then`) should trigger.

They are introduced as a list inside the `when` clause.

Conditions are evaluated sequentially. The list represents a logical OR. ANY
single condition block evaluating to true will trigger the rule consequence

Each condition consists of a dictionary of clauses. The condition evaluates to
true only if ALL its clauses are satisfied.

Each clause can specify a number of possible matches. The clause will be
satisfied if ANY of the possibilities is an actual match

```
...
when:
  # condition 1 -- true for branch master of repo1 OR repo2
  - repo: [ repo1, repo2 ]
    branch: master

  # condition 2 -- true for branches master and develop of any repo
  - branch: [ master, develop ]

  # condition 3 -- true for branches master and develop of repo1
  - repo: repo1
    branch: [ master, develop ]
  ...
```

#### Regex match

Clauses can also match with regexes:

    - branch: /release-.+/

Will match any branch or tag starting with the text "release-"

In the case of a regex match, it's possible to tag that match so that it can
be used as a key in parameter maps (see example of usage below).

    - branch:
        match: /release-.+/
        as: release_TAG

### Rule consequences

Consequences of the rules belong inside the `then` section, that's a list inside
the clause.

There are two possible classes of consequences: `add_action` and
`configure_action` . The first one creates new actions, the second allows to
modify previously added actions.

```
...
then:
  - add_action:
    ...
  - configure_action:
    ...
  - add_action:
    ...
```

Consequences are evaluated sequentially. Actions are executed after parsing and
evaluating the complete rules file.

### `add_action` rule class

When adding an action, you specify `name`, `parameters`, `action` and an
`enabled` flag.

* The `name` of the parameter should be unique across the rules file. Two actions
with the same name cannot be added in the same run.

* The `enabled` flag indicates whether the action will actually run, it is
  disabled by default

* The `action` clause is the action definition. It consists of `class_name` and
  `arguments`. The contents of the arguments will vary depending on the action
  class.

* The `parameters` clause is a dictionary of parameters that will be passed to
  the action. Parameters can be defined in several ways.

  The simplest is static value assignation.

      parameter: value

  Values can use variable substitution from the execution context, i.e:

      parameter: "${env[ENV_VAR]}"

  Another option is usage of maps, i.e:

      parameter:
        key: branch
        map:
          master: value1
          development: value2
          release_TAG: value3

  Supported keys can be any value present in the context.

  Note the usage of `release_TAG`, which was defined as a clause matching alias
  when we were covering regex matches in clauses.

Parameters can be referenced in the definition of the action by using the
`{parameter}` syntax.

## Available action classes

### CommandAction

Takes the following arguments:

* `env`: a dictionary with environment variables.
* `command`: a string with the command to be executed, the command is parsed
  through the system shell.

## The Context object

Throughout the evaluation of the rules file, references can be made to values
in the context. The context contains information about the environment where
the deployment director is running in.

This is approximately what the context object would look like if we exported it
to YAML:

```
branch: ... # <the branch/tag provided by the CI>
repo: ... # <the name of the repository provided by the CI>
ci:
  # all the bits of information provided by the CI
  # i.e. Codeship provides
  branch: ...
  build_id: ...
  committer_email: ...
  committer_name: ...
  committer_username: ...
  commit_description: ...
  commit_id: ...
  commit_message: ...
  name: ...
  project_id: ...
  repo_name: ...
  string_time: ...
  timestamp: ...
env:
  # environment variables
  PATH: ...
  HOME: ...
  ...
```

## Which CI/CD are supported

- Codeship
