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
  
  event_df <- aggregate(event_onset, 
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


#' This function binds the existing data in FED3 with what's recorded using TDT

bind_fed_events <- function(FED_data, exp_start, exp_stop, fed3_event_onset){
  
  recorded_events <- nrow(filter(FED_data, data.table::between(datetime, exp_start, exp_stop)))
  
  tdt_events <- tryCatch(
    expr = {
        fedwatcher_tdt(fed3_event_onset, exp_start)
        #message("Trials found")
    },
    error = function(e){
        message('Error found')
        print(e)
        # give empty data frame so we can call nrow()
        data.frame()
    },
    warning = function(w){
        message('Caught a warning!')
        print(w)
    },
    finally = {
        #message('All done, quitting.')
    }
    )    

  if (!assertthat::are_equal(
    x = recorded_events,
    y = nrow(tdt_events)
  )){
    usethis::ui_info("tdt_events {length(tdt_events)} and FED_data {nrow(recorded_events)} filtered during trial do not have the same number of events, using FED_data only")
    usethis::ui_info("Check the input and/or use `match_datetimes()`")
    # return FED_data only
    joint_pellet_data <- FED_data %>% 
      filter(data.table::between(datetime, exp_start, exp_stop)) %>% 
      mutate(event = 1:n(),
             tdt_datetime=datetime,
             seconds=as.numeric(datetime - first(datetime))) %>% 
      fed3::filter_pellets()
    return(joint_pellet_data)
  } else{
    if(recorded_events == 0 && length(fed3_event_onset) == 0){
      usethis::ui_warn("Event length matches and there were no events in FED_data and fed3_event_onset")
      joint_pellet_data <- tibble(tdt_datetime = numeric(), event = numeric(), seconds  = numeric(), Pellet_Count = numeric())
      return(joint_pellet_data)
    } else{
      tdt_data <- fedwatcher_tdt(fed3_event_onset, trial_start = exp_start)
      joint_pellet_data <- FED_data %>% 
        filter(data.table::between(datetime, exp_start, exp_stop)) %>% 
        mutate(event = 1:n()) %>% 
        left_join(tdt_data, by="event") %>% 
        fed3::filter_pellets()
      return(joint_pellet_data)
    }
    
  }
  
}


# USE THIS FUNCTION IF datetimes in the FED don't match with tdt
# usage: match_datetimes(FED_data$datetime, tdt_data$tdt_datetime)
# returns a data.frame with the matching dates and the column `indices` will give you the indices to subset from FED_data

match_datetimes <- function(dt, pattern) {
  # calculate the diffs
  dt_diff <- diff(dt)
  pattern_diff <- diff(pattern)
  window <- length(pattern)
  before <- floor(window/2)
  after <- floor(window/2) - 1
  result <- slider::slide_dbl(dt_diff,
                              .f = ~sum(abs(as.numeric((.x - pattern_diff)))),
                              .before = before,
                              .after = after,
                              .complete = T)
  # find min and add one
  center <- which.min(result) + 1
  indices <- seq(from = center - window/2, to = center + window/2 - 1, by = 1)
  return(tibble::tibble(indices = indices, dt = dt[indices], pattern))
}
