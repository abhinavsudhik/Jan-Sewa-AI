# Requirements Document: Jan Sewa AI

## Introduction

Jan Sewa AI is a Voice-First Multimodal AI Agentic Ecosystem designed to democratize access to government services in Bharat (India). The system shifts from passive government portals to an Active Agentic Ecosystem that autonomously completes complex tasks like document retrieval, form filling, and scheme discovery for users with limited digital literacy. The system leverages Google Agent Development Kit (ADK), Gemini 2.5 Pro, India Stack APIs (DigiLocker, Bhashini), and advanced privacy-preserving techniques to provide inclusive, secure, and proactive governance services.

## Glossary

- **Jan_Sewa_AI**: The complete Voice-First Multimodal AI Agentic Ecosystem
- **Orchestrator**: The primary AI agent powered by Gemini 2.5 Pro that coordinates all sub-agents and workflows
- **Agent_Executor**: Component responsible for autonomous task execution using Google ADK
- **Scheme_Matchmaker**: AI agent that proactively discovers and suggests eligible welfare schemes
- **Bhashini_Adapter**: Integration layer for Bhashini APIs handling multilingual speech and text
- **Legal_Translator**: RAG-based component that simplifies complex legal language
- **Privacy_Shield**: Local-first security architecture that protects user PII
- **Vision_Agent**: Gemini Computer Use model that interacts with legacy portals
- **DigiLocker_Connector**: Integration component for accessing user documents from DigiLocker
- **India_Stack**: Collection of APIs including DigiLocker, Bhashini, and other government digital infrastructure
- **PII**: Personally Identifiable Information (Aadhaar, phone numbers, addresses, etc.)
- **RAG**: Retrieval-Augmented Generation for context-aware AI responses
- **User_Profile**: Structured data containing user demographics, location, income, and preferences
- **Workflow**: End-to-end task sequence (e.g., retrieving driving license, applying for pension)
- **Legacy_Portal**: Government websites without modern APIs (e-District, UMANG, etc.)
- **DLP**: Data Loss Prevention / Sensitive Data Protection service from Google Cloud

## Requirements

### Requirement 1: Active Agentic Execution

**User Story:** As a user with limited digital literacy, I want the system to autonomously complete government tasks on my behalf, so that I can access services without navigating complex portals.

#### Acceptance Criteria

1. WHEN a user requests a government service via voice, THE Orchestrator SHALL decompose the request into a structured workflow with discrete steps
2. WHEN a workflow is created, THE Agent_Executor SHALL autonomously execute each step using Google ADK agents without requiring user intervention
3. WHEN executing a workflow step, THE Agent_Executor SHALL interact with government portals, APIs, or legacy systems to complete the action
4. WHEN a workflow step completes successfully, THE Agent_Executor SHALL proceed to the next step in the sequence
5. IF a workflow step fails, THEN THE Agent_Executor SHALL retry up to 3 times with exponential backoff before escalating to the user
6. WHEN a workflow requires user input (OTP, consent), THE Orchestrator SHALL pause execution and request the specific information via voice
7. WHEN a workflow completes, THE Orchestrator SHALL provide a voice summary of the outcome and any retrieved documents
8. THE Agent_Executor SHALL support workflows for document retrieval (driving license, PAN card, birth certificate) and form submissions (pension applications, ration card updates)

### Requirement 2: Scheme Matchmaker (Proactive Discovery)

**User Story:** As a user, I want the system to automatically identify welfare schemes I'm eligible for, so that I don't miss benefits due to lack of awareness.

#### Acceptance Criteria

1. WHEN a user profile is created or updated, THE Scheme_Matchmaker SHALL analyze the profile data against a database of government welfare schemes
2. WHEN analyzing eligibility, THE Scheme_Matchmaker SHALL retrieve supporting documents from DigiLocker (income certificate, caste certificate, location proof)
3. WHEN a user matches eligibility criteria for a scheme, THE Scheme_Matchmaker SHALL calculate a confidence score between 0 and 100
4. WHEN eligible schemes are identified, THE Scheme_Matchmaker SHALL rank them by relevance (confidence score, benefit amount, application deadline)
5. WHEN proactively notifying users, THE Orchestrator SHALL present the top 3 eligible schemes via voice in the user's preferred language
6. WHEN presenting a scheme, THE Orchestrator SHALL explain eligibility criteria, benefits, required documents, and application steps in simplified language
7. THE Scheme_Matchmaker SHALL support major welfare schemes including PM-Kisan, Ayushman Bharat, pension schemes, and state-specific programs
8. WHEN scheme eligibility rules change, THE Scheme_Matchmaker SHALL re-evaluate all user profiles within 24 hours

### Requirement 3: Multi-Dialect Bhashini Integration

**User Story:** As a user who speaks a regional language or dialect, I want to interact with the system in my native language, so that I can communicate naturally without language barriers.

#### Acceptance Criteria

1. WHEN a user initiates a voice interaction, THE Bhashini_Adapter SHALL detect the spoken language and dialect from the first utterance
2. WHEN processing speech input, THE Bhashini_Adapter SHALL convert speech to text using Bhashini Speech-to-Text APIs with support for 22+ Indian languages
3. WHEN generating voice responses, THE Bhashini_Adapter SHALL convert text to speech using Bhashini Text-to-Speech APIs in the user's detected language
4. WHEN a user switches languages mid-conversation (code-mixing like Hinglish or Malayalam-English), THE Bhashini_Adapter SHALL detect the switch and adapt within 2 seconds
5. THE Bhashini_Adapter SHALL support seamless dialect switching for major language variants (Hindi dialects, Tamil dialects, etc.)
6. WHEN speech recognition confidence is below 70%, THE Bhashini_Adapter SHALL request clarification from the user in their language
7. WHEN Bhashini APIs are unavailable, THE Bhashini_Adapter SHALL fallback to cached language models for the 5 most common languages (Hindi, English, Tamil, Telugu, Bengali)
8. THE Bhashini_Adapter SHALL maintain conversation context across language switches to preserve workflow continuity

### Requirement 4: Legal-Speak Translator

**User Story:** As a user with limited education, I want complex legal terms and government disclaimers explained in simple language, so that I can understand what I'm agreeing to.

#### Acceptance Criteria

1. WHEN the system encounters legal text or government disclaimers, THE Legal_Translator SHALL identify complex legal terminology and clauses
2. WHEN simplifying legal text, THE Legal_Translator SHALL use RAG to retrieve relevant explanations from a curated knowledge base
3. WHEN generating simplified explanations, THE Legal_Translator SHALL produce text at a 5th-grade reading level as measured by Flesch-Kincaid score
4. WHEN translating legal text, THE Legal_Translator SHALL preserve the original legal meaning and intent without distortion
5. WHEN presenting simplified text, THE Orchestrator SHALL provide both the original legal text and the simplified version via voice
6. THE Legal_Translator SHALL support simplification in all 22+ languages supported by the Bhashini_Adapter
7. WHEN legal text contains critical obligations or rights, THE Legal_Translator SHALL highlight these with emphasis in the voice output
8. WHEN the knowledge base lacks context for specific legal terms, THE Legal_Translator SHALL use Gemini 2.5 Pro to generate explanations and flag them for human review

### Requirement 5: Zero-Trust Privacy Shield

**User Story:** As a user concerned about privacy, I want my sensitive personal information protected, so that my data is not exposed or misused during processing.

#### Acceptance Criteria

1. WHEN user data is collected, THE Privacy_Shield SHALL process and store all PII locally on the user's device before any cloud transmission
2. WHEN data must be sent to cloud services, THE Privacy_Shield SHALL scan for sensitive PII using Google Cloud DLP APIs
3. WHEN PII is detected in outbound data, THE Privacy_Shield SHALL automatically redact or mask the sensitive information (Aadhaar numbers, phone numbers, addresses)
4. WHEN masking PII, THE Privacy_Shield SHALL use format-preserving tokenization to maintain data utility for processing
5. WHEN receiving data from cloud services, THE Privacy_Shield SHALL re-hydrate masked tokens with original PII only on the local device
6. THE Privacy_Shield SHALL maintain an audit log of all PII access, masking, and transmission events locally on the device
7. WHEN a user requests data deletion, THE Privacy_Shield SHALL permanently erase all local PII and revoke all cloud-stored tokens within 24 hours
8. THE Privacy_Shield SHALL encrypt all local PII storage using AES-256 encryption with device-specific keys
9. WHEN DigiLocker documents are accessed, THE Privacy_Shield SHALL cache documents locally and redact PII before any AI processing
10. THE Privacy_Shield SHALL never transmit unmasked Aadhaar numbers, biometric data, or financial account numbers to cloud services

### Requirement 6: Vision-Action Portal Automation

**User Story:** As a user trying to access legacy government portals, I want the system to interact with these portals on my behalf, so that I don't need to navigate complex interfaces.

#### Acceptance Criteria

1. WHEN a workflow requires interaction with a legacy portal, THE Vision_Agent SHALL capture screenshots of the portal interface
2. WHEN analyzing portal interfaces, THE Vision_Agent SHALL use Gemini Computer Use model to identify interactive elements (buttons, forms, dropdowns)
3. WHEN filling forms, THE Vision_Agent SHALL extract required field labels and input appropriate data from the user profile
4. WHEN clicking buttons or links, THE Vision_Agent SHALL verify the action completed successfully by analyzing the resulting page
5. WHEN encountering CAPTCHAs, THE Vision_Agent SHALL request user assistance via voice to solve the challenge
6. WHEN portal navigation fails, THE Vision_Agent SHALL retry the action up to 3 times before reporting failure to the Orchestrator
7. THE Vision_Agent SHALL support major legacy portals including e-District, UMANG, state-specific portals, and transport department websites
8. WHEN interacting with portals, THE Vision_Agent SHALL respect rate limits and implement delays between actions to avoid detection as automated traffic
9. WHEN a portal session expires, THE Vision_Agent SHALL detect the timeout and re-authenticate automatically using stored credentials
10. THE Vision_Agent SHALL log all portal interactions with screenshots for audit and debugging purposes

### Requirement 7: DigiLocker Integration

**User Story:** As a user, I want the system to access my government documents from DigiLocker, so that I don't need to manually upload documents for verification.

#### Acceptance Criteria

1. WHEN a user first uses the system, THE DigiLocker_Connector SHALL initiate OAuth 2.0 authentication flow with DigiLocker
2. WHEN authentication succeeds, THE DigiLocker_Connector SHALL store the access token securely using the Privacy_Shield
3. WHEN a workflow requires document verification, THE DigiLocker_Connector SHALL retrieve the specific document from DigiLocker APIs
4. WHEN retrieving documents, THE DigiLocker_Connector SHALL fetch only the minimum required documents for the current workflow
5. WHEN a document is retrieved, THE Privacy_Shield SHALL cache it locally and redact PII before any AI processing
6. WHEN DigiLocker access token expires, THE DigiLocker_Connector SHALL automatically refresh the token using the refresh token
7. THE DigiLocker_Connector SHALL support retrieval of all major document types (Aadhaar, PAN, driving license, education certificates, income certificates)
8. WHEN DigiLocker APIs are unavailable, THE DigiLocker_Connector SHALL allow users to manually upload documents via voice-guided instructions

### Requirement 8: Multi-Agent Orchestration

**User Story:** As a system architect, I want a modular multi-agent architecture, so that the system is maintainable, scalable, and can evolve with new capabilities.

#### Acceptance Criteria

1. THE Orchestrator SHALL coordinate all specialized agents (Agent_Executor, Scheme_Matchmaker, Vision_Agent, Legal_Translator) using Google ADK
2. WHEN a user request is received, THE Orchestrator SHALL determine which agents are required and their execution sequence
3. WHEN agents execute, THE Orchestrator SHALL pass context and data between agents using a structured message format
4. WHEN multiple agents can execute in parallel, THE Orchestrator SHALL run them concurrently to minimize latency
5. THE Orchestrator SHALL maintain conversation state and workflow progress across multiple user interactions
6. WHEN an agent fails, THE Orchestrator SHALL implement fallback strategies or alternative agents to complete the workflow
7. THE Orchestrator SHALL monitor agent performance metrics (latency, success rate, error types) and log them for analysis
8. THE Orchestrator SHALL support dynamic agent registration to allow new capabilities to be added without system redesign

### Requirement 9: Voice-First User Interface

**User Story:** As a user with limited digital literacy, I want to interact with the system entirely through voice, so that I can access services without reading or typing.

#### Acceptance Criteria

1. WHEN a user speaks, THE Jan_Sewa_AI SHALL continuously listen for voice input using wake word detection or push-to-talk
2. WHEN processing voice input, THE Jan_Sewa_AI SHALL provide immediate audio feedback (beep, tone) to confirm input is being processed
3. WHEN generating responses, THE Jan_Sewa_AI SHALL use natural conversational voice output with appropriate pacing and pauses
4. WHEN presenting multiple options, THE Jan_Sewa_AI SHALL number them clearly and allow users to respond with numbers or natural language
5. WHEN users make errors or provide unclear input, THE Jan_Sewa_AI SHALL ask clarifying questions in a supportive, non-judgmental tone
6. THE Jan_Sewa_AI SHALL support voice commands for common actions (repeat, go back, cancel, help)
7. WHEN workflows are long, THE Jan_Sewa_AI SHALL provide progress updates every 30 seconds to maintain user engagement
8. WHEN critical information is presented (OTP, confirmation numbers), THE Jan_Sewa_AI SHALL repeat it twice and offer to send it via SMS

### Requirement 10: Offline Capability and Resilience

**User Story:** As a user in areas with poor connectivity, I want the system to work offline when possible, so that I can still access basic services during network outages.

#### Acceptance Criteria

1. WHEN network connectivity is unavailable, THE Jan_Sewa_AI SHALL continue to function for cached workflows and previously accessed data
2. WHEN operating offline, THE Jan_Sewa_AI SHALL use locally stored language models for the 5 most common languages
3. WHEN connectivity is restored, THE Jan_Sewa_AI SHALL synchronize any pending workflow actions and user data with cloud services
4. WHEN a workflow requires cloud services and connectivity is unavailable, THE Jan_Sewa_AI SHALL queue the workflow and notify the user of the delay
5. THE Jan_Sewa_AI SHALL cache frequently accessed scheme information, legal translations, and portal navigation patterns locally
6. WHEN network quality is poor (high latency, packet loss), THE Jan_Sewa_AI SHALL adapt by reducing data transfer and using compressed formats
7. THE Jan_Sewa_AI SHALL detect network availability changes within 5 seconds and adjust functionality accordingly
8. WHEN operating in offline mode, THE Privacy_Shield SHALL continue to protect PII using local encryption and access controls

### Requirement 11: Accessibility and Inclusivity

**User Story:** As a user with disabilities, I want the system to accommodate my needs, so that I can access government services independently.

#### Acceptance Criteria

1. WHEN users have hearing impairments, THE Jan_Sewa_AI SHALL provide text-based alternatives to all voice interactions
2. WHEN users have visual impairments, THE Jan_Sewa_AI SHALL provide detailed voice descriptions of all visual content and navigation options
3. WHEN users have motor impairments, THE Jan_Sewa_AI SHALL support voice-only interaction without requiring any physical input
4. THE Jan_Sewa_AI SHALL adjust speech rate, volume, and pitch based on user preferences
5. WHEN users have cognitive disabilities, THE Jan_Sewa_AI SHALL use simplified language, shorter sentences, and more frequent confirmations
6. THE Jan_Sewa_AI SHALL support assisted mode where a helper can interact on behalf of the user with explicit consent
7. WHEN presenting information, THE Jan_Sewa_AI SHALL avoid time-based interactions that require quick responses
8. THE Jan_Sewa_AI SHALL comply with WCAG 2.1 Level AA accessibility guidelines for any visual interfaces

### Requirement 12: Security and Authentication

**User Story:** As a user, I want my account and data to be secure, so that unauthorized parties cannot access my information or perform actions on my behalf.

#### Acceptance Criteria

1. WHEN a user first registers, THE Jan_Sewa_AI SHALL authenticate the user using Aadhaar-based authentication or mobile OTP
2. WHEN a user returns, THE Jan_Sewa_AI SHALL support biometric authentication (voice biometrics, fingerprint) for quick access
3. WHEN performing sensitive actions (document access, form submission), THE Jan_Sewa_AI SHALL require step-up authentication via OTP
4. THE Jan_Sewa_AI SHALL implement session timeouts of 15 minutes for inactive sessions
5. WHEN suspicious activity is detected (unusual location, multiple failed attempts), THE Jan_Sewa_AI SHALL lock the account and notify the user
6. THE Jan_Sewa_AI SHALL encrypt all data in transit using TLS 1.3 or higher
7. WHEN storing credentials or tokens, THE Jan_Sewa_AI SHALL use secure storage mechanisms provided by the device operating system
8. THE Jan_Sewa_AI SHALL implement rate limiting to prevent brute force attacks (max 5 failed attempts per hour)
9. WHEN users share devices, THE Jan_Sewa_AI SHALL support multiple user profiles with separate authentication
10. THE Jan_Sewa_AI SHALL comply with IT Act 2000 and Digital Personal Data Protection Act 2023 requirements

### Requirement 13: Performance and Scalability

**User Story:** As a system operator, I want the system to handle high user loads efficiently, so that all users receive timely service during peak usage.

#### Acceptance Criteria

1. WHEN processing voice input, THE Jan_Sewa_AI SHALL respond with initial acknowledgment within 2 seconds
2. WHEN executing simple workflows (document retrieval), THE Jan_Sewa_AI SHALL complete the task within 30 seconds
3. WHEN executing complex workflows (form submission with multiple steps), THE Jan_Sewa_AI SHALL complete the task within 3 minutes
4. THE Jan_Sewa_AI SHALL support at least 10,000 concurrent users per deployment region
5. WHEN user load increases, THE Jan_Sewa_AI SHALL automatically scale cloud resources to maintain performance SLAs
6. THE Jan_Sewa_AI SHALL maintain 99.5% uptime excluding scheduled maintenance
7. WHEN APIs or external services are slow, THE Jan_Sewa_AI SHALL implement timeouts and provide user feedback within 10 seconds
8. THE Jan_Sewa_AI SHALL cache frequently accessed data (scheme information, portal navigation patterns) to reduce latency

### Requirement 14: Monitoring and Observability

**User Story:** As a system administrator, I want comprehensive monitoring and logging, so that I can troubleshoot issues and optimize system performance.

#### Acceptance Criteria

1. THE Jan_Sewa_AI SHALL log all user interactions, workflow executions, and agent actions with timestamps and correlation IDs
2. WHEN errors occur, THE Jan_Sewa_AI SHALL capture detailed error context including stack traces, input data, and system state
3. THE Jan_Sewa_AI SHALL emit metrics for key performance indicators (response time, success rate, user satisfaction)
4. WHEN system health degrades, THE Jan_Sewa_AI SHALL trigger alerts to administrators via configured channels
5. THE Jan_Sewa_AI SHALL provide dashboards showing real-time system status, user activity, and workflow success rates
6. WHEN analyzing logs, THE Privacy_Shield SHALL ensure all PII is redacted before logs are stored or transmitted
7. THE Jan_Sewa_AI SHALL retain logs for 90 days for troubleshooting and compliance purposes
8. THE Jan_Sewa_AI SHALL support distributed tracing to track requests across multiple agents and services

### Requirement 15: Scheme Database Management

**User Story:** As a system administrator, I want to easily update the scheme database, so that users always have access to current welfare programs.

#### Acceptance Criteria

1. THE Jan_Sewa_AI SHALL maintain a structured database of government welfare schemes with eligibility criteria, benefits, and application procedures
2. WHEN new schemes are announced, THE Jan_Sewa_AI SHALL support adding scheme definitions through a configuration interface
3. WHEN scheme rules change, THE Jan_Sewa_AI SHALL support updating eligibility criteria without code changes
4. THE Jan_Sewa_AI SHALL validate scheme definitions for completeness and consistency before activation
5. WHEN schemes expire or are discontinued, THE Jan_Sewa_AI SHALL automatically deactivate them and stop suggesting them to users
6. THE Jan_Sewa_AI SHALL support versioning of scheme definitions to track changes over time
7. WHEN scheme data is updated, THE Scheme_Matchmaker SHALL re-evaluate affected user profiles within 24 hours
8. THE Jan_Sewa_AI SHALL support importing scheme data from government APIs or structured data sources

