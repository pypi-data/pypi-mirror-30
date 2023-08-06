from basematic.pipelines.Node_Pipeline import node_pipeline

from basematic.pipelines.DropSeq import CB_split
from basematic.pipelines.DropSeq import CB_stats
from basematic.pipelines.DropSeq import CB_counts

node = node_pipeline("DropSeq")
node.desc = "Pipeline for Hightroughput single-cell RNA-Seq, 10X inDrop and Drop-Seq"

node.add_node("cbCounts", CB_counts.node)
node.add_node("cbStats", CB_stats.node)
node.add_node("cbSplits", CB_split.node)
node.add_node("starAligns", "HAHAHHA!!!")
node.add_node("tagging", "HAHAHHA!!!")
node.add_node("aggregate", "HAHAHHA!!!")

node.add_config("protocol", "Protocol", "Method used, can be 10X, inDrop or DropSeq")
node.add_config("min_reads", "Mininum Reads Counts", "Minimum reads to be used")

node.add_connection(CB_split.out_splitFiles, "STAR......")

print(CB_counts.node.logic)