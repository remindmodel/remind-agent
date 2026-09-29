#!/usr/bin/env Rscript
# gdx_inspect.R -- context-safe structural summary of a (potentially huge) GDX file.
#
# Two axes of "huge" are guarded:
#   * RECORDS -- metadata read first (records = FALSE); records loaded for ONE symbol at a time.
#   * SYMBOLS -- a model GDX (fulldata.gdx) has ~1700 symbols. Default output is a class-count
#                headline; per-symbol listing only when the (optionally --grep-filtered) set is
#                small; and the tool never auto-deep-dives every parameter.
# Output stays bounded regardless of file size.
#
# Usage:
#   source /p/system/modulefiles/defaults/piam/module_load_piam
#   Rscript gdx_inspect.R <file.gdx> [symbol] [--grep=<regex>] [--list]
#     symbol        exact symbol to deep-dive
#     --grep=<re>   restrict inventory + parameter deep-dive to names matching <re>
#     --list        force the full per-symbol inventory even when large

suppressMessages({
  library(gamstransfer)
  library(dplyr)
  library(tidyr)
  library(purrr)
  library(stringr)
  library(glue)
  library(rlang)     # set_names(); rlang %||% too, if needed (base %||% is R 4.4+, cluster is 4.3.2)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("usage: Rscript gdx_inspect.R <file.gdx> [symbol] [--grep=<re>] [--list]")
path <- args[[1]]
rest <- args[-1]
if (!file.exists(path)) stop("file not found: ", path)

getSym <- function(container, nm) container$getSymbols(nm)[[1]]  # R6 Container has no [[ accessor

grepHits   <- str_subset(rest, "^--grep=")
grepPat    <- if (length(grepHits)) str_remove(grepHits[[1]], "^--grep=") else ""
forceList  <- "--list" %in% rest
positional <- str_subset(rest, "^--", negate = TRUE)
focus      <- if (length(positional)) positional[[1]] else NA_character_
LISTMAX <- 40L   # max symbols to list line-by-line
DIVEMAX <- 12L   # max parameters to auto-deep-dive with no focus/grep

writeLines(glue("== FILE    : {path}"))
writeLines(glue("== on disk : {round(file.info(path)$size / 1024^2, 3)} MB"))

## 1) metadata-only inventory --------------------------------------------------
meta <- Container$new()
meta$read(path, records = FALSE)

inv <- tibble(name = meta$listSymbols()) |>
  mutate(
    sym    = map(name, \(n) getSym(meta, n)),
    class  = map_chr(sym, \(s) class(s)[[1]]),
    dim    = map_int(sym, \(s) as.integer(s$dimension)),
    domain = map_chr(sym, \(s) str_flatten(s$domainNames, collapse = ","))
  )

writeLines(glue("== symbols : {nrow(inv)}"))
writeLines(c("", "== by class:"))
inv |> count(class, name = "n") |> arrange(desc(n)) |> print()

shown <- if (nzchar(grepPat)) filter(inv, str_detect(name, grepPat)) else inv
if (nzchar(grepPat)) writeLines(c("", glue("matching /{grepPat}/ : {nrow(shown)}")))

if (forceList || nrow(shown) <= LISTMAX) {
  shown |> select(name, class, dim, domain) |> print(n = Inf)
} else {
  writeLines(c("", glue(
    "({nrow(shown)} symbols too many to list; pass a symbol name, --grep=<regex>, or --list)"
  )))
}

## 2) deep dive (records read one symbol at a time) ---------------------------
params  <- inv |> filter(class == "Parameter") |> pull(name)
targets <-
  if (!is.na(focus)) {
    intersect(focus, inv$name)
  } else if (nzchar(grepPat)) {
    intersect(shown$name, params)
  } else if (length(params) <= DIVEMAX) {
    params
  } else {
    writeLines(c("", glue(
      "{length(params)} parameters -- not deep-diving all; narrow with a symbol name or --grep=<regex>."
    )))
    character(0)
  }

describe_dim <- function(r, d) {
  lab <- as.character(r[[d]])
  num <- suppressWarnings(as.numeric(lab))
  if (all(!is.na(num))) {
    glue("  {str_pad(d, 9)}: {n_distinct(num)} unique, range [{min(num)} .. {max(num)}]")
  } else {
    u   <- unique(lab)
    ell <- if (length(u) > 6) ", ..." else ""
    glue("  {str_pad(d, 9)}: {length(u)} unique, e.g. {str_flatten(head(u, 6), ', ')}{ell}")
  }
}

deep_dive <- function(nm) {
  one <- Container$new()
  one$read(path, symbols = nm, records = TRUE)     # only this symbol's records enter memory
  r   <- as_tibble(getSym(one, nm)$records)
  cls <- inv |> filter(name == nm) |> pull(class)
  writeLines(c("", glue("################ {nm} ({cls}) ################")))
  if (nrow(r) == 0) { writeLines("(no records)"); return(invisible()) }

  valueCols <- c("value", "level", "marginal", "lower", "upper", "scale", "element_text")
  dimCols   <- setdiff(names(r), valueCols)
  writeLines(glue("dims: {str_flatten(dimCols, ' x ')} | records: {format(nrow(r), big.mark = ',')}"))
  walk(dimCols, \(d) writeLines(describe_dim(r, d)))

  if (!("value" %in% names(r))) {
    writeLines(glue("  (non-parameter: {str_flatten(intersect(valueCols, names(r)), '/')} - skipping numeric summary)"))
    return(invisible())
  }

  v  <- r$value
  nz <- sum(v == 0, na.rm = TRUE)
  writeLines(glue(
    "  value    : min {signif(min(v), 4)} | mean {signif(mean(v), 4)} | max {signif(max(v), 4)} | ",
    "zeros {format(nz, big.mark = ',')} ({round(100 * nz / length(v), 1)}%) | NA {sum(is.na(v))}"
  ))
  box <- prod(map_dbl(dimCols, \(d) n_distinct(r[[d]])))
  writeLines(glue(
    "  fill     : stored {format(nrow(r), big.mark = ',')} / {format(box, big.mark = ',')} box cells = ",
    "{round(100 * nrow(r) / box, 1)}% | nonzero {round(100 * sum(v != 0) / box, 1)}%"
  ))

  # triangularity + adaptive mean-value shape map for 2 numeric dims
  nums <- map(set_names(dimCols), \(d) suppressWarnings(as.numeric(as.character(r[[d]]))))
  if (length(dimCols) == 2 && all(!is.na(nums[[1]])) && all(!is.na(nums[[2]]))) {
    a <- nums[[dimCols[[1]]]]; b <- nums[[dimCols[[2]]]]
    tri <- tibble(a, b, v) |>
      summarise(lt = sum(a < b), lt_nz = sum(a < b & v != 0),
                eq = sum(a == b),
                gt = sum(a > b), gt_nz = sum(a > b & v != 0))
    writeLines(glue(
      "  triangle : {dimCols[[1]]}<{dimCols[[2]]}: {tri$lt} (nz {tri$lt_nz}) | ==: {tri$eq} | ",
      "{dimCols[[1]]}>{dimCols[[2]]}: {tri$gt} (nz {tri$gt_nz})"
    ))

    span   <- max(max(a) - min(a), max(b) - min(b))
    binw   <- if (span / 10 <= 12) 10 else if (span / 25 <= 12) 25 else 50
    maxabs <- suppressWarnings(max(abs(v[v != 0])))
    e      <- if (is.finite(maxabs) && maxabs > 0) floor(log10(maxabs)) else 0
    writeLines(glue(
      "  shape map: MEAN value in units of 1e{e} | rows = {dimCols[[1]]} ({binw}-yr bins), ",
      "cols = {dimCols[[2]]} | NA = no records"
    ))
    tibble(rb = (a %/% binw) * binw, cb = (b %/% binw) * binw, v) |>
      group_by(rb, cb) |>
      summarise(m = round(mean(v) / 10^e, 2), .groups = "drop") |>
      pivot_wider(names_from = cb, values_from = m, names_sort = TRUE) |>
      arrange(rb) |>
      print(n = Inf)
  }

  writeLines("  sample:")
  print(head(r, 4))
}

walk(targets, deep_dive)
