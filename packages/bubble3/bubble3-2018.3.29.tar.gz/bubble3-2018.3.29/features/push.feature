Feature: Bubble pull,transform,push
Scenario: Given a target service in configuration
    Given a new working directory
    When I run "bubble3 init"
    When I run "bubble3 pull"
    When I run "bubble3 transform"
    When I run "bubble3 push"
    Then the command output should contain "Pushing"
    Then the command output should contain "saved result in ["
    And the command returncode is "0"

Scenario: Given a target service in configuration only DEV stage
    Given a new working directory
    When I run "bubble3 init"
    When I run "bubble3 pull"
    When I run "bubble3 transform"
    When I run "bubble3 push -s PROD"
    Then the command output should contain "There is no STAGE in CFG:PROD"
    And the command returncode is "1"
