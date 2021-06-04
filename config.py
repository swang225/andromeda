import os
import os.path as osp

MODEL_DIR=os.environ.get("ANDROMEDA", osp.join(osp.dirname(__file__), 'model'))
