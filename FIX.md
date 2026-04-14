# Refactoring Plan: Migrating from Pickle/Cloudpickle to Msgpack

This document outlines the technical strategy to eliminate insecure deserialization vulnerabilities in the `google-cloud-aiplatform` SDK by replacing `pickle` and `cloudpickle` with **Msgpack**.

## 1. Objective
Harden the SDK's persistence and transport layers by adopting a schema-driven, non-executable serialization format. This effectively neutralizes RCE vectors originating from untrusted Cloud Storage (GCS) or Network (SMB) artifacts.

## 2. Dependency Management
- **Add Dependency**: Add `msgpack >= 1.0.0` to `setup.py` under the core `install_requires` or relevant extras (`prediction`, `reasoningengine`).
- **Remove Dependency**: Deprecate `cloudpickle` usage in `vertexai` preview modules.

## 3. Implementation Strategy

### Phase 0: Environment & Branch Management
- **Action**: Create a dedicated security branch to isolate the refactoring changes.
- **Command**: 
  ```bash
  git checkout -b security/fix-rce-msgpack-migration
  ```

### Phase 1: Harden Static Predictors (`pickle`)
Target: `google/cloud/aiplatform/prediction/`
- **Action**: Replace `pickle.load` and `joblib.load` with `msgpack.unpackb`.
- **Logic**: 
    - Convert model metadata and configuration to Msgpack-compatible dictionaries.
    - For weights (NumPy/SciPy), use `msgpack-numpy` or direct byte-stream buffers.
- **Files**:
    - `google/cloud/aiplatform/prediction/sklearn/predictor.py`
    - `google/cloud/aiplatform/prediction/xgboost/predictor.py`

### Phase 2: Secure Dynamic Engines (`cloudpickle`)
Target: `vertexai/agent_engines/` and `vertexai/reasoning_engines/`
- **Challenge**: `cloudpickle` is used to ship live Python code. `msgpack` is data-only.
- **Action**: 
    - Separate **Logic** from **State**. 
    - Use `msgpack` for the state (variables, parameters).
    - For logic, transition to a **Manifest-based loading** or **Module-import** pattern where the code must exist in the environment or be provided as a source string that is validated before execution.
- **Files**:
    - `vertexai/agent_engines/_agent_engines.py`
    - `vertexai/reasoning_engines/_reasoning_engines.py`

### Phase 3: Metadata and Transport Hardening
Target: `google/cloud/aiplatform/metadata/`
- **Action**: Replace debug/logging `pickle.dumps` in GRPC transports with `msgpack.packb`.
- **Files**:
    - `google/cloud/aiplatform/metadata/_models.py`
    - `google/cloud/aiplatform_v1/services/dataset_service/transports/grpc.py`

### Phase 4: Code Hygiene & Formatting
- **Action**: Enforce Google-specific code style across all modified files to ensure maintainability and compliance with the upstream repository.
- **Tools**:
    - `isort`: Standardize import ordering.
    - `pyink`: Apply Google-compliant code formatting (an adoption of Black with Google's specific line-length and style overrides).

---

## 4. Security Enhancements (The "Double Lock")

### A. Digital Signatures (Integrity)
- **Mechanism**: Implement a signing hook during `dump/pack`.
- **Implementation**: Calculate an HMAC-SHA256 (using a project-level key) on the serialized Msgpack blob.
- **Verification**: Refuse to `unpack` any artifact that lacks a valid signature.

### B. URI/Path Sanitization
- **Mechanism**: Block UNC/SMB paths.
- **Action**: Modify `google/cloud/aiplatform/utils/prediction_utils.py` and `path_utils.py` to:
    - Strictly enforce `gs://` or local filesystem paths.
    - Explicitly deny paths starting with `\\` or containing `smb://` protocols.

---

## 5. Verification Plan
1. **Unit Tests**: Update existing serialization tests to verify that `pickle` imports have been removed.
2. **Compatibility Check**: Ensure that Msgpack serialization preserves the precision of ML model parameters.
3. **Exploit Regression**: Verify that the SMB-based PoC from `GUIDE.md` now fails with a "Format not supported" or "Signature missing" error.

---
*Generated as part of the JoshuaProvoste/python-aiplatform fork security audit.*
