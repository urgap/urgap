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

parser$add_argument(
  "-d", "--design",
  help = "design",
  required = FALSE,
  default = "~rep + condition"
)

parser$add_argument(
  "-r", "--ref",
  help = "reference",
  required = FALSE,
  default = "WT"
)

parser$add_argument(
  "--alpha",
  help = "alpha",
  required = FALSE,
  default = 0.05
)

parser$add_argument(
  "--plotPCA_intgroup",
  help = "interaction group for PCA plotting",
  required = FALSE,
  default = 'c("condition", "rep")'
)

parser$add_argument(
  "--plotMA_ylim",
  help = "limits for y-axis in MA plot",
  required = FALSE,
  default = "c(-5,5)"
)

parser$add_argument(
  "--plotMA_ylab",
  help = "label for y-axis in MA plot",
  required = FALSE,
  default = "Log2 fold change"
)

parser$add_argument(
  "--plotMA_xlab",
  help = "label for x-axis in MA plot",
  required = FALSE,
  default = "Mean expression"
)

args <- parser$parse_args()

count_data <- read.csv(args$input[1], header = TRUE, sep = ",")
col_data <- read.csv(args$input[2], header = TRUE, sep = ",")

dds <- DESeqDataSetFromMatrix(
  countData = count_data,
  colData = col_data,
  design = eval(parse(text = args$design)))

dds <- dds[rowSums(counts(dds)) > 1, ]

dds$condition <- relevel(dds$condition, ref = args$ref)

dds <- DESeq(dds)

res <- results(dds, alpha = args$alpha)

res <- res[order(res$padj), ]

if (!is.null(args$query_string) && nzchar(args$query_string)) {
  res_sig <- subset(res, eval(parse(text = args$query_string)))
  res_df <- as.data.frame(res_sig)
} else {
  res_df <- as.data.frame(res)
}

res_df <- cbind(row.names(res_df), res_df)

colnames(res_df)[1] <- "GeneID"

write.table(
  res_df,
  file = args$output[1],
  sep = ",",
  row.names = FALSE,
  col.names = TRUE)

rld <- rlog(dds)
pdf(args$output[2])
plotPCA(rld, intgroup = eval(parse(text = args$plotPCA_intgroup)))
dev.off()

pdf(args$output[3])
plotMA(
  res,
  xlab = args$plotMA_xlab,
  ylab = args$plotMA_ylab,
  ylim = eval(parse(text = args$plotMA_ylim)))
dev.off()