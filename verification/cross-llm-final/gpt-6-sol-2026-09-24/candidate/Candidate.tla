------------------------------ MODULE Candidate ------------------------------
(* NVMe Base Specification 2.3, 2025-08-01, Figure 41 (printed 62/PDF 86)
 * and Figure 42 (printed 64/PDF 88). Normal CC.EN operation only.
 * Finite abstraction: two opaque Admin Queue configurations and at most two
 * processed and posted command events per enable interval. Counts are ghost
 * histories, not hardware registers. Reset initiation starts a new interval.
 * No shutdown, fatal error, timeout, transport state, full reset effects, or
 * undefined host writes are represented. *)
EXTENDS Naturals

(* AdminTokens are opaque, distinct configurations of AQA/ASQ/ACQ. *)
AdminTokens == {"adminA", "adminB"}
MaxWork == 2

VARIABLES
    ccEn,           \* CC.EN bit 0; host writes, initially zero.
    cstsRdy,        \* CSTS.RDY bit 0; controller writes, initially zero.
    adminConfig,    \* Opaque AQA/ASQ/ACQ tuple, preserved on Controller Reset.
    processedCount, \* Ghost: commands processed in the current enable interval.
    completedCount  \* Ghost: CQ entries posted in the current enable interval.

vars == <<ccEn, cstsRdy, adminConfig, processedCount, completedCount>>

TypeOK ==
    /\ ccEn \in {0, 1}
    /\ cstsRdy \in {0, 1}
    /\ adminConfig \in AdminTokens
    /\ processedCount \in 0..MaxWork
    /\ completedCount \in 0..MaxWork
    /\ completedCount <= processedCount

(* The reset values of CC.EN and CSTS.RDY are zero. The source pages do not
 * specify initial AQA/ASQ/ACQ values; either abstract token is permitted. *)
Init ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ adminConfig \in AdminTokens
    /\ processedCount = 0
    /\ completedCount = 0

(* REQ-CC-EN: legal host enable requires RDY=0. The forbidden case RDY=1
 * has undefined results and is excluded from this normal-operation model. *)
HostEnable ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ ccEn' = 1
    /\ UNCHANGED <<cstsRdy, adminConfig, processedCount, completedCount>>

(* REQ-RDY: controller eventually becomes ready after a legal enable. *)
ControllerReady ==
    /\ ccEn = 1
    /\ cstsRdy = 0
    /\ cstsRdy' = 1
    /\ UNCHANGED <<ccEn, adminConfig, processedCount, completedCount>>

(* REQ-NO-WORK: processing and posting are separate observable events. *)
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

(* REQ-ADMIN-PRESERVE: legal host clear initiates Controller Reset. RDY may
 * remain one. Ghost histories restart here; Admin Queue properties persist. *)
HostDisable ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ ccEn' = 0
    /\ processedCount' = 0
    /\ completedCount' = 0
    /\ UNCHANGED <<cstsRdy, adminConfig>>

(* REQ-RDY: the controller signals readiness for re-enable after reset. *)
ControllerResetDone ==
    /\ ccEn = 0
    /\ cstsRdy = 1
    /\ cstsRdy' = 0
    /\ UNCHANGED <<ccEn, adminConfig, processedCount, completedCount>>

(* REQ-ADMIN-WRITE: Admin Queue properties can change only with CC.EN=0. *)
HostWriteAdmin ==
    /\ ccEn = 0
    /\ adminConfig' \in AdminTokens \ {adminConfig}
    /\ UNCHANGED <<ccEn, cstsRdy, processedCount, completedCount>>

Next == HostEnable \/ ControllerReady \/ ProcessCommand \/ PostCompletion
        \/ HostDisable \/ ControllerResetDone \/ HostWriteAdmin

(* ASSUME-PROGRESS: in normal operation a continuously enabled controller
 * ready/reset-complete step eventually occurs. Host actions are not fair. *)
Spec == Init /\ [][Next]_vars
        /\ WF_vars(ControllerReady)
        /\ WF_vars(ControllerResetDone)

(* REQ-NO-WORK: independent transition check using persistent ghost histories.
 * The bit is read in the pre-state; a reset initiated while enabled may clear
 * histories, but no transition out of a disabled state may process/post. *)
NoWorkWhileDisabled ==
    [][ccEn = 0 => UNCHANGED <<processedCount, completedCount>>]_vars

(* REQ-ADMIN-PRESERVE: detect reset start/end by CC.EN and RDY falling edges. *)
AdminPreservedOnReset ==
    [][((ccEn = 1 /\ ccEn' = 0) \/ (cstsRdy = 1 /\ cstsRdy' = 0))
       => adminConfig' = adminConfig]_vars

(* REQ-ADMIN-WRITE: a change of the opaque Admin Queue configuration must
 * begin in a disabled state, regardless of which action performs it. *)
AdminWritesOnlyDisabled ==
    [][(adminConfig' # adminConfig) => ccEn = 0]_vars

(* REQ-RDY: conditional progress, with the controller fairness above. *)
EnableEventuallyReady == (ccEn = 1) ~> (cstsRdy = 1)
ResetEventuallyDone == (ccEn = 0 /\ cstsRdy = 1) ~> (cstsRdy = 0)
=============================================================================
