#!/bin/bash
POD="root@YOUR_POD_IP"
PORT="YOUR_PORT"
KEY="$HOME/.ssh/id_ed25519"
LOCAL="$(dirname "$0")/CRISP-Real2Sim/inputs/checkpoints/body_models"
REMOTE="/workspace/CRISP-pipeline/CRISP-Real2Sim"

echo "=== Transferring SMPL files ==="
scp -P $PORT -i $KEY \
  $LOCAL/smpl/SMPL_FEMALE.pkl \
  $LOCAL/smpl/SMPL_MALE.pkl \
  $LOCAL/smpl/SMPL_NEUTRAL.pkl \
  $POD:$REMOTE/inputs/checkpoints/body_models/smpl/

scp -P $PORT -i $KEY \
  $LOCAL/smpl/SMPL_FEMALE.pkl \
  $LOCAL/smpl/SMPL_MALE.pkl \
  $LOCAL/smpl/SMPL_NEUTRAL.pkl \
  $POD:$REMOTE/prep/data/smpl/

scp -P $PORT -i $KEY \
  $LOCAL/smpl/SMPL_FEMALE.pkl \
  $LOCAL/smpl/SMPL_MALE.pkl \
  $LOCAL/smpl/SMPL_NEUTRAL.pkl \
  $POD:$REMOTE/prep/HMR/inputs/checkpoints/body_models/smpl/

echo "=== Transferring SMPLX files ==="
scp -P $PORT -i $KEY \
  $LOCAL/smplx/SMPLX_FEMALE.npz \
  $LOCAL/smplx/SMPLX_MALE.npz \
  $LOCAL/smplx/SMPLX_NEUTRAL.npz \
  $POD:$REMOTE/inputs/checkpoints/body_models/smplx/

scp -P $PORT -i $KEY \
  $LOCAL/smplx/SMPLX_FEMALE.npz \
  $LOCAL/smplx/SMPLX_MALE.npz \
  $LOCAL/smplx/SMPLX_NEUTRAL.npz \
  $POD:$REMOTE/prep/data/smplx/

scp -P $PORT -i $KEY \
  $LOCAL/smplx/SMPLX_FEMALE.npz \
  $LOCAL/smplx/SMPLX_MALE.npz \
  $LOCAL/smplx/SMPLX_NEUTRAL.npz \
  $POD:$REMOTE/prep/HMR/inputs/checkpoints/body_models/smplx/

echo "=== ALL DONE ==="
