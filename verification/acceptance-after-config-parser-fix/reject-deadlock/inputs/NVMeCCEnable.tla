-------------------------- MODULE NVMeCCEnable --------------------------
(*
 * NVMe controller enable handshake - bounded reference model.
 * Source: NVMe Base Specification 2.3, 2025-08-01.
 * Section 3.1.4.5 / Figure 41, p.62 / PDF p.86 (CC.EN).
 * Section 3.1.4.6 / Figure 42, p.64 / PDF p.88 (CSTS.RDY).
 *
 * Scope: normal-operation enable/disable handshake, disabled work prohibition,
 * and preservation of an abstract Admin Queue property across Controller Reset.
 * See source.json for requirements, assumptions and exclusions.
 * This is not a full NVMe controller or a full Controller Reset model.
 *)
EXTENDS Naturals, FiniteSets

(* CONSTANTS - exploration choices, not hardware limits.
 * ASSUME-BOUND: bounded number of processing events over the entire trace.
 * ASSUME-ADMIN: opaque tokens stand for prevalidated Admin Queue settings. *)
CONSTANTS
    MaxOperations,       (* positive integer; tested at 1, 2, 3 *)
    AdminConfigValues,   (* finite nonempty set of abstract config tokens *)
    InitialAdminConfig   (* one member; initial setting is a model assumption *)

ASSUME /\ MaxOperations \in Nat
       /\ MaxOperations > 0
       /\ IsFiniteSet(AdminConfigValues)
       /\ InitialAdminConfig \in AdminConfigValues

(* VARIABLES - domain, ownership, initialization and persistence.
 * ccEn: bit, host write, initial 0; HostDisable clears it.
 * cstsRdy: bit, controller write, initial 0; clears when reset finishes.
 * adminConfig: AdminConfigValues, host; initial InitialAdminConfig;
 *              survives enable/disable/reset, writable only while ccEn=0.
 * commandPhase: ghost abstraction of one command, initially "idle";
 *               reset discards in-flight work (ASSUME-COMMAND).
 * processedCount/completedCount: 0..MaxOperations, persistent ghost histories;
 *              initial 0, never reset; observe processing/posting events.
 *)
VARIABLES ccEn, cstsRdy, adminConfig, commandPhase,
          processedCount, completedCount

vars == <<ccEn, cstsRdy, adminConfig, commandPhase,
          processedCount, completedCount>>

CommandPhases == {"idle", "submitted", "processed"}

TypeOK ==
    /\ ccEn \in {0, 1}
    /\ cstsRdy \in {0, 1}
    /\ adminConfig \in AdminConfigValues
    /\ commandPhase \in CommandPhases
    /\ processedCount \in 0..MaxOperations
    /\ completedCount \in 0..MaxOperations

(* REQ-CC-EN / REQ-RDY: documented reset bits are 0.
 * ASSUME-INITIAL: begin after reset has completed with no in-flight work. *)
Init ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ adminConfig = InitialAdminConfig
    /\ commandPhase = "idle"
    /\ processedCount = 0
    /\ completedCount = 0

(* REQ-CC-EN: valid host enable from the disabled/ready-to-enable state.
 * Source: Figure 41, p.62. ASSUME-NORMAL excludes undefined host toggles. *)
HostEnable ==
    /\ ccEn = 0
    /\ cstsRdy = 0
    /\ ccEn' = 1
    /\ UNCHANGED <<cstsRdy, adminConfig, commandPhase,
                    processedCount, completedCount>>

(* REQ-RDY: controller asserts readiness after enable, not atomically with it.
 * Source: Figures 41/42, p.62/p.64. ASSUME-NORMAL excludes shutdown/errors. *)
ControllerReady ==
    /\ ccEn = 1
    /\ cstsRdy = 0
    /\ cstsRdy' = 1
    /\ UNCHANGED <<ccEn, adminConfig, commandPhase,
                    processedCount, completedCount>>

(* REQ-CC-EN and REQ-ADMIN-PRESERVE: clearing EN initiates reset.
 * Source: Figure 41, p.62. ASSUME-COMMAND abstracts in-flight work disposal;
 * complete reset effects on queues/transport/features are out of scope. *)
HostDisable ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ ccEn' = 0
    /\ commandPhase' = "idle"
    /\ UNCHANGED <<cstsRdy, adminConfig, processedCount, completedCount>>

(* REQ-RDY: clear RDY once ready to be re-enabled.
 * Source: Figure 42, p.64. Intermediate ccEn=0,cstsRdy=1 is permitted. *)
ControllerResetDone ==
    /\ ccEn = 0
    /\ cstsRdy = 1
    /\ cstsRdy' = 0
    /\ UNCHANGED <<ccEn, adminConfig, commandPhase,
                    processedCount, completedCount>>

(* REQ-ADMIN-WRITE: Admin Queue properties are modifiable only when disabled.
 * Source: Figure 41, p.62. ASSUME-ADMIN treats a property tuple as one token. *)
HostConfigure ==
    /\ ccEn = 0
    /\ \E config \in AdminConfigValues \ {adminConfig} :
           adminConfig' = config
    /\ UNCHANGED <<ccEn, cstsRdy, commandPhase, processedCount, completedCount>>

(* ASSUME-COMMAND/BOUND: one abstract command at a time with a lifetime budget.
 * REQ-RDY (Figure 42, p.64): cooperative host submits only after readiness.
 * No opcode/transport/layout/completion-status semantics are claimed. *)
SubmitCommand ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ commandPhase = "idle"
    /\ processedCount < MaxOperations
    /\ commandPhase' = "submitted"
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, processedCount, completedCount>>

(* REQ-NO-WORK: processing is forbidden with EN=0 (Figure 41, p.62).
 * ASSUME-COMMAND: represent a processing event by one persistent increment. *)
ProcessCommand ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ commandPhase = "submitted"
    /\ processedCount < MaxOperations
    /\ commandPhase' = "processed"
    /\ processedCount' = processedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, completedCount>>

(* REQ-NO-WORK: posting completions is forbidden with EN=0 (Figure 41, p.62).
 * ASSUME-COMMAND: at most one post for each abstract processed command. *)
CompleteCommand ==
    /\ ccEn = 1
    /\ cstsRdy = 1
    /\ commandPhase = "processed"
    /\ commandPhase' = "idle"
    /\ completedCount' = completedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, processedCount>>

Next == FALSE /\ UNCHANGED vars

(* ASSUME-PROGRESS: weak fairness for the two hardware handshake responses.
 * No wall-clock timeout is claimed. Host and command fairness are not assumed. *)
Spec ==
    /\ Init
    /\ [][Next]_vars
    /\ WF_vars(ControllerReady)
    /\ WF_vars(ControllerResetDone)

(* S1: CompleteCountBounded - ASSUME-COMMAND consistency.
 * A completion must have a preceding processing event in this abstraction. *)
CompleteCountBounded == completedCount <= processedCount

(* S2: NoWorkWhileDisabled - REQ-NO-WORK, Figure 41, p.62.
 * A pre-state with EN=0 must not permit either observable work event.
 * Histories remain nonzero after prior work; they are not current activity. *)
NoWorkWhileDisabled ==
    [][ccEn = 0 =>
        UNCHANGED <<processedCount, completedCount>>]_vars

(* S3: AdminPreservedOnReset - REQ-ADMIN-PRESERVE, Figure 41, p.62.
 * Detect initiation/completion edges independently of their action bodies. *)
AdminPreservedOnReset ==
    [][((ccEn = 1 /\ ccEn' = 0) \/ (cstsRdy = 1 /\ cstsRdy' = 0))
        => adminConfig' = adminConfig]_vars

(* S4: AdminWritesOnlyDisabled - REQ-ADMIN-WRITE, Figure 41, p.62. *)
AdminWritesOnlyDisabled ==
    [][ccEn = 1 => adminConfig' = adminConfig]_vars

(* L1/L2: REQ-RDY, Figures 41/42, p.62/p.64, under ASSUME-PROGRESS.
 * Conditional progress only; this does not prove NVMe timeout compliance. *)
EnableEventuallyReady == (ccEn = 1 /\ cstsRdy = 0) ~> (cstsRdy = 1)
ResetEventuallyDone == (ccEn = 0 /\ cstsRdy = 1) ~> (cstsRdy = 0)

(* Test-only reachability probes, absent from production .cfg.
 * Expected violations witness meaningful completion and reset-pending states. *)
NoCompletionReached == completedCount = 0
NoResetPendingReached == ~(ccEn = 0 /\ cstsRdy = 1)
=============================================================================
