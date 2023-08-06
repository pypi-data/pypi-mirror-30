Feature: Bubble pump(pull,transform,push)
Scenario: Given a target service in configuration
    Given a new working directory
    When I run "bubble3 init"
    When I run "bubble3 pump"
    Then the command output should contain "Pushing"
    Then the command output should contain "saved result in ["
    And the command returncode is "0"
    
