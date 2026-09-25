------------------------------ MODULE Candidate ------------------------------
(***************************************************************************
 * Finite normal-operation model of NVMe CC.EN and CSTS.RDY.
 * Source: NVM Express Base Specification, Revision 2.3 (2025-08-01),
 * Figures 41 and 42, printed pages 62 and 64 / PDF pages 86 and 88.
 * Shutdown, fatal errors, timeouts, transport behavior, full reset details,
 * and host writes whose results are undefined are outside this model.
*)
EXTENDS Naturals

CONSTANT MaxWork

ASSUME MaxWork \in Nat \ {0}

VARIABLES
    ccEn,             \* CC.EN hardware bit, written by the host
    cstsRdy,          \* CSTS.RDY hardware bit, written by the controller
    adminConfig,      \* finite abstraction of AQA/ASQ/ACQ properties
    processedCount,   \* ghost history: commands processed
    completedCount    \* ghost history: completion entries posted

vars == <<ccEn, cstsRdy, adminConfig, processedCount, completedCount>>

AdminConfigs == {"AdminA", "AdminB"}

TypeOK ==
    /\ ccEn \in {0, 1}
    /\ cstsRdy \in {0, 1}
    /\ adminConfig \in AdminConfigs
    /\ processedCount \in 0..MaxWork
    /\ completedCount \in 0..MaxWork
    /\ completedCount <= processedCount

Init ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ adminConfig = "AdminA"
    /\ processedCount = 0
    /\ completedCount = 0

(***************************************************************************
 * REQ-CC-EN / REQ-RDY: a defined normal-operation enable write occurs only
 * while RDY is zero; the controller later reports ready.
*)
HostEnable ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ ccEn' = 1
    /\ UNCHANGED <<cstsRdy, adminConfig, processedCount, completedCount>>

BecomeReady ==
    /\ ccEn = 1
    /\ cstsRdy = 0
    /\ cstsRdy' = 1
    /\ UNCHANGED <<ccEn, adminConfig, processedCount, completedCount>>

(***************************************************************************
 * REQ-NO-WORK: processing and completion posting occur only while enabled
 * and ready. Counts are bounded observer histories, not hardware registers.
*)
ProcessCommand ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ processedCount < MaxWork
    /\ processedCount' = processedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, completedCount>>

PostCompletion ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ completedCount < processedCount
    /\ completedCount' = completedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, processedCount>>

(***************************************************************************
 * REQ-ADMIN-PRESERVE: a defined disable write starts Controller Reset and
 * preserves the abstracted Admin Queue properties. RDY may remain one.
*)
HostDisable ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ ccEn' = 0
    /\ UNCHANGED <<cstsRdy, adminConfig, processedCount, completedCount>>

FinishReset ==
    /\ ccEn = 0
    /\ cstsRdy = 1
    /\ cstsRdy' = 0
    /\ UNCHANGED <<ccEn, adminConfig, processedCount, completedCount>>

(***************************************************************************
 * REQ-ADMIN-WRITE: the host may modify the abstracted Admin Queue
 * properties only while CC.EN is zero, including reset-pending states.
*)
AdminWrite ==
    /\ ccEn = 0
    /\ adminConfig' \in AdminConfigs \ {adminConfig}
    /\ UNCHANGED <<ccEn, cstsRdy, processedCount, completedCount>>

Next ==
    \/ HostEnable
    \/ BecomeReady
    \/ ProcessCommand
    \/ PostCompletion
    \/ HostDisable
    \/ FinishReset
    \/ AdminWrite

(***************************************************************************
 * ASSUME-PROGRESS: in normal operation, a continuously enabled controller
 * readiness transition eventually occurs. CAP.TO timing is not modeled.
*)
Spec ==
    /\ Init
    /\ [][Next]_vars
    /\ WF_vars(BecomeReady)
    /\ WF_vars(FinishReset)

NoWorkWhileDisabled ==
    [][ccEn = 0 => UNCHANGED <<processedCount, completedCount>>]_vars

AdminPreservedOnReset ==
    [][((ccEn = 1 /\ ccEn' = 0) \/
            (cstsRdy = 1 /\ cstsRdy' = 0)) =>
           adminConfig' = adminConfig]_vars

AdminWritesOnlyDisabled ==
    [][adminConfig' # adminConfig => ccEn = 0]_vars

EnableEventuallyReady == (ccEn = 1) ~> (cstsRdy = 1)

ResetEventuallyDone == (ccEn = 0 /\ cstsRdy = 1) ~> (cstsRdy = 0)

=============================================================================
