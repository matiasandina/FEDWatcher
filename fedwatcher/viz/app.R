library(shiny)
library(shinyFiles)
library(bslib)
library(tidyverse)
library(DT)


# aesthetics --------------------------------------------------------------
#fedwatcher_theme <- 
#bs_theme(
#    version = version_default(),
#    bootswatch = "minty",#"darkly",
#    bg = "#424547",
#    fg = "#E1ECF2"
#)

fedwatcher_theme <-
bs_theme() %>% 
bs_theme_update(bg = "#424547",
                fg = "#E1ECF2",
                font_scale = NULL, 
                # darkly messes up the navbar color
                # not sure how to change
                bootswatch = "minty", 
                )

# Helper functions --------------------------------------------------------

get_public_ip <- function(){
    ip <- suppressWarnings(
        read.csv("https://ipinfo.io/ip", 
             header = F, 
             stringsAsFactors = F)[1,1]
    )
    return(ip)
}

get_local_ip <- function(interface="wlp2s0"){
    # this will fail in the Rpi
    ip <- system("ifconfig", intern=T)
    line <-  stringr::str_which(string = ip,
                                pattern = interface) + 1
    ip <- stringr::str_squish(ip[line])
    ip <- stringr::str_split(ip, pattern = " ")[[1]][2]
    return(ip)
}

# read configs ------------------------------------------------------------
read_config <- function(files_in_dir){
    # expecting list of full paths to .ini configs
    # reading
    config_list <- map(files_in_dir, configr::read.config)
    # casting into df twice (cols within each config, rows between configs)
    config_df <- map_df(config_list, bind_cols)
    return(config_df)
}


# UI ----------------------------------------------------------------------
ui <- fluidPage(
    theme = fedwatcher_theme,
    # Application title
    #titlePanel(div(img(src="64.png"), "FEDWatcher")),
    #tags$head(HTML("<title>FEDWatcher</title>")), #Without company logo
    tags$head(HTML("<title>FEDWatcher</title> <link rel='icon' type='image/gif/png' href='64.png'>")), #WIth company logo
    navbarPage(title = div(img(src="64.png", 
                               style="margin-top: -5px;", 
                               height = 50), "FEDWatcher"),
               theme = fedwatcher_theme),

    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
        h5("Select your FEDWatcher project folder"),
        shinyDirButton('directory', 'Select a folder', 'Please select a folder', FALSE, icon = icon("folder")),
        h5("You Selected"),
        verbatimTextOutput("directorypath"),
        h5("Available `config.ini` files on directory"),
        selectizeInput(inputId = "config_list",
                       label = HTML("Select from sessions to pool together.
                       <br/>
                       Delete options using DEL or Backspase Keys."),
                       choices = c("All"),
                       multiple = TRUE,
                       options = list(
                           'plugins' = list('remove_button'),
                           'create' = TRUE,
                           'persist' = TRUE)),
        hr(),
        downloadButton('downloadData', 'Download data')
        ),
        mainPanel(
            h5("Configuration files available"),
            hr(),
            DT::dataTableOutput("config_table"),
            h5("Some text here"),
            #gt_output(outputId = "config_table")
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output, session) {
    volumes <- c(Home = fs::path_home(), "R Installation" = R.home(), getVolumes()())
    shinyDirChoose(input, "directory", roots = volumes,
                   session = session, restrictions = system.file(package = "base"))
    
    #output$config_table <- renderDataTable(mtcars)
    values <- reactiveValues(config_df = NULL)
    
    output$directorypath <- renderPrint({
        cat("No directory has been selected yet")
    })
    
    # directory input -------------
    observeEvent(input$directory,
                 {
                     # print the dir  
                     output$directorypath <- renderPrint({
                         if (is.integer(input$directory)) {
                             cat("No directory has been selected yet")
                         } else {
                             parseDirPath(volumes, input$directory)
                         }
                     })
                     # scan contents
                     if (!is.integer(input$directory)) {
                         files_in_dir <- list.files(parseDirPath(volumes, input$directory),
                                                    pattern = "config.+ini$", 
                                                    full.names = T)
                         # update options
                         updateSelectizeInput(session, 'config_list', choices = c("All", basename(files_in_dir)),
                                              server = TRUE)
                         values$config_df <- read_config(files_in_dir)
                         # df rendering ----
                         req(is.null(values$config_df) == FALSE)
                         output$config_table <- DT::renderDataTable(
                             # datetime gets shown in UTC, using formatdate messes with the buttons
                             DT::datatable(values$config_df, 
                                       style = "bootstrap4",
                                       extensions = "FixedHeader",
                                       options = list(fixedHeader=T) 
                                       #options = list(dom = 't')
                                       )
                         )

                         if (identical(files_in_dir, character(0))) {
                             showNotification("No config.ini files in chosen directory. Please choose another one", 
                                              duration = 30, type = "error")
                         }
                     }
                     
                 }
    )
    
    # parse selection
    parse_selection <- function(config_list, out_length){
        # returns a boolean of length out_length
        # we will use this boolean to highlight cells and subset configs
        if (is.null(config_list)) {
            selection <- rep(0, out_length)
        }
        else if (config_list == "All") {
            selection <- rep(1, out_length)
        } else {
            found <- stringr::str_extract(config_list, pattern = "[0-9]+")
            selection <- sapply(found, function(x) grepl(x, values$config_df$session_num)) %>%
                # keep dimensions of at least 2 cols in case there's only one match
                as_tibble() %>% 
                mutate(zero = 0) %>% 
                rowSums()
        }
        return(selection)
    }
    
    # Observe selection of configs
    observeEvent(input$config_list,{
        req(is.null(values$config_df) == FALSE)
        parsed <- parse_selection(input$config_list, nrow(values$config_df))
        values$config_df <- values$config_df %>% 
            mutate(sel = parsed)
        output$config_table <- renderDataTable(
            # datetime gets shown in UTC, using formatdate messes with the buttons
            datatable(values$config_df , 
                      style = "bootstrap4",
                      extensions = "FixedHeader",
                      options = list(fixedHeader=T,
                                     columnDefs = list(list(targets = ncol(values$config_df), visible = FALSE)))
                      #options = list(dom = 't')
            ) %>% formatStyle(
                "sel",
                target = 'row',
                backgroundColor = styleEqual(c(0, 1), c("#424547", 'yellow')))
        )
    }, 
    # this is key so when we have nothing selected it will still update
    ignoreNULL = FALSE)
    
    # read data -----------------------
    read_selected <- function(){
        # filter
        parsed <- parse_selection(input$config_list, nrow(values$config_df))
        selected_df <- values$config_df[parsed, ]
        # work on the filtered df
        # CAUTION: This will have the hardcoded path on data capture!
        # meaning it will only find files in the Raspberry pi
        exp_dir <- unique(selected_df$exp_dir)
        years <- lubridate::year(selected_df$exp_end)
        years <- years[complete.cases(years)]
        m_s <- stringr::str_pad(
            string = lubridate::month(selected_df$exp_end),
            width = 2,pad = 0)
        m_s <- m_s[complete.cases(m_s)]
        path_df <- tidyr::expand_grid(years, m_s) %>% 
            mutate(exp_dir = exp_dir,
                   path = file.path(exp_dir, years, m_s))
        fed_files <- purrr::map(path_df$path,
                   function(tt)
                   list.files(tt, pattern = "^FED.+[CcSsVv]$",
                              full.names = T)) %>% 
            unlist()
        print(fed_files)
        fed_data <- purrr::map_df(fed_files,
                                  fed3::read_fed)
        return(fed_data)
    }
    
    # download data -----------------------------------------------------------
    output$downloadData <- downloadHandler(
        filename = function() { 
            paste0(unique(basename(values$config_df$exp_dir)),
                  "_FED_pooled_data.csv")
        },
        content = function(file) {
            fed_data <- read_selected()
            print(fed_data)
            readr::write_csv(fed_data, file)
        })
    

}

# Run the application 
env <- "dev"
#env <- "prod"

host <- 
switch (env,
    prod = {get_local_ip()},
    dev = {nsl("localhost")}
    
)
    
options(shiny.host = host)
options(shiny.port = NULL)
shinyApp(ui = ui, server = server)