library(slj)
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  filename <- args[1]
  print("!!!")
  slj_ipsum_generator(filename)
}

main()