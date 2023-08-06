Feature: Bubble usage
Scenario: Starting bubble
    Given a new working directory
    When I run "bubble3 --help"
    Then the command output should contain "Usage"
    And  the command returncode is "0"