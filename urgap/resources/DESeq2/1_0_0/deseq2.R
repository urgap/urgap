library(DESeq2)
library(argparse)

parser <- ArgumentParser()

parser$add_argument(
  "-i", "--input",
  help = "Input file",
  action = "append",
  required = TRUE
)

parser$add_argument(
  "-o", "--output",
  help = "Output file",
  action = "append",
  required = TRUE
)

parser$add_argument(
  "-q", "--query_string",
  help = "Query string",
  required = FALSE
)

args <- parser$parse_args()

countData <- read.csv(args$input[1], header = TRUE, sep = ",")
colData <- read.csv(args$input[2], header = TRUE, sep = ",")

dds <- DESeqDataSetFromMatrix (countData = countData,colData = colData, design = ~rep + condition)

dds <- dds[ rowSums(counts(dds)) > 1, ]

dds$condition <- relevel(dds$condition, ref = "WT")

dds <- DESeq(dds)

res <- results(dds, alpha = 0.05)

res <- res[order(res$padj), ]

if (!is.null(args$query_string) && nzchar(args$query_string)) {
  res_sig <- subset(res, eval(parse(text = args$query_string)))
  resDF <- as.data.frame(res_sig)
} else {
  resDF <- as.data.frame(res)
}

resDF <- cbind(row.names(resDF), resDF)

colnames(resDF)[1] <- "GeneID"

write.table(resDF, file = args$output[1], sep = ",", row.names = F, col.names = T)

rld <- rlog(dds)
pdf(args$output[2])
plotPCA(rld, intgroup = c("condition", "rep"))
dev.off()

pdf(args$output[3])
plotMA(res, xlab = "Mean expression",  ylab ="Log2 fold change",  ylim = c(-5,5), main = "DESeq2")
dev.off()