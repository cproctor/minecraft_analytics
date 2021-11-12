from segment.product.transcript import SegmentTranscript
from segment.product.video import SegmentVideo
from segment.product.logs import SegmentLogs
from segment.product.trace import SegmentTrace
from segment.product.joint_attention import SegmentJointAttention

PRODUCT_FORMATS = {
    'transcript': SegmentTranscript,
    'video': SegmentVideo,
    'logs': SegmentLogs,
    'trace': SegmentTrace,
    'joint_attention': SegmentJointAttention,
}

