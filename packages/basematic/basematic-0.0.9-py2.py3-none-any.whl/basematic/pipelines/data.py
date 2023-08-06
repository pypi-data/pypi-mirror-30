from .QC import data as QC
from .CNV import data as CNV
from .FastRNA import data as FastRNA
from .RNASeq import data as RNAseq
from .DropSeq import _index as DropSeq
from .Panel import  data as panel

data = {
    "type" : "basedata",
    "node" : [
        {"id" : "QC", "type" : QC.data},
        {"id" : "CNV", "type" : CNV.data},
        {"id" : "FastRNA", "type" : FastRNA.data},
        {"id" : "RNA-Seq", "type" : RNAseq.data},
        {"id" : "DropSeq", "type" : DropSeq.data},
        {"id" : "Panel_pipeline", "type" : panel.data}
    ]
}