# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Service Query Recognition
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Scope the property to concrete failing cases: queries about "data access" and "status tracking" services
  - Test that queries containing service keywords (["data", "access"], ["status", "tracking"]) return either a service guide or "coming soon" message
  - The test assertions should match: result contains service_guide OR result.message contains "coming soon"
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found (e.g., "data access request" returns only welcome message instead of service guide)
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Existing Aadhaar, Session, and Language Handling
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs:
    - "aadhaar name change" queries return the Aadhaar service guide
    - Generic greetings ("hello", "hi") return the welcome message
    - Session IDs are generated (new UUID) or preserved (if provided)
    - Language fields are preserved in responses
  - Write property-based tests capturing observed behavior patterns:
    - For all queries with "aadhaar" AND "name" keywords, verify service guide is returned
    - For all generic greetings, verify welcome message is returned
    - For all requests without session_id, verify new UUID is generated
    - For all requests with session_id, verify same session_id is in response
    - For all language values, verify language is preserved in response
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Fix for chat query response bug

  - [ ] 3.1 Implement the fix in process_chat function
    - Add service keyword mapping dictionary (map keywords to service IDs in MOCK_SERVICES)
    - Map ["data", "access"] → "data_access_request"
    - Map ["status", "tracking"] → "service_status_tracking"
    - Keep ["aadhaar", "name"] → "aadhaar_name_change"
    - Implement flexible keyword matching loop (check all service keyword patterns)
    - Add "coming soon" response for queries matching keywords but service not in MOCK_SERVICES
    - Preserve existing session ID generation logic
    - Preserve existing language field handling
    - Maintain welcome message as final fallback for unclear queries
    - _Bug_Condition: isBugCondition(input) where input contains service keywords (["data", "access"], ["status", "tracking"]) but NOT ("aadhaar" AND "name")_
    - _Expected_Behavior: For all inputs where isBugCondition(input), result contains service_guide OR result.message contains "coming soon"_
    - _Preservation: For all inputs where NOT isBugCondition(input), behavior matches original function (Aadhaar queries, generic greetings, session ID generation, language handling)_
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

  - [ ] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Service Query Recognition
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Existing Aadhaar, Session, and Language Handling
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
