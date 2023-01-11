# This function can be used to transform the timestamps 
# from TDT system  
# library(reticulate)
# if FED connected to PtC0
# py$block['epocs']['PtC0']['onset']
# trial_start <- py$block["info"]['start']
#' @param event_onset vector with onset timestamps in seconds from TDT block
#' @return A `data.frame` with 
#' #' \itemize{
#'   \item event - The number of event.
#'   \item seconds - The first recorded timestamp of the event.
#'   \item tdt_datetime - If `trial_start` is `POSIXct`, a `POSIXct` timestamp will be calculated using the `seconds` column.
#' }
#' 
fedwatcher_tdt <- function(event_onset, trial_start=NULL){
  if(identical(event_onset, list())){
    stop("event_onset is an empty `list`, fedwatcher_tdt() cannot calculate if no events were provided")
  }
  # we believe two real events can't be 0.01 seconds apart
  event_threshold <- 0.01
  # diff will remove the first event, so we add it
  # cumsum will give us clusters
  cluster_values <- cumsum(c(1, diff(event_onset)) > event_threshold)
  event_number <- length(unique(cluster_values))
  # we could do a formal clustering approach 
  # hclust works well, kmeans is unstable
  # cutree(hclust(dist(event_onset)),k = event_number)
  
  event_df <- aggregate(fed3_event_onset, 
                        by = list(event = cluster_values), 
                        FUN = min)
  event_df <- dplyr::rename(event_df, seconds = x)
  
  # Transform seconds into datetime
  if(lubridate::is.POSIXct(trial_start)){
    usethis::ui_info("Trial start provided at {trial_start}, adding `tdt_datetime` column.")
    event_df$tdt_datetime <- trial_start + lubridate::seconds(event_df$seconds)
  }
  
  return(event_df)
}
