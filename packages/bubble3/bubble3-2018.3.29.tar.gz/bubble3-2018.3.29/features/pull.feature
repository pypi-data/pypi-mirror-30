Feature: Bubble pull
Scenario: Given a source service in configuration
    Given a new working directory
    When I run "bubble3 init"
    When I run "bubble3 pull"
    Then the command output should contain "saved result in ["
    And the command returncode is "0"

Scenario: Given a source service in configuration with only DEV
    Given a new working directory
    When I run "bubble3 init"
    When I run "bubble3 pull -s PROD"
    Then the command output should contain "There is no STAGE in CFG:PROD"
    And the command returncode is "1"
