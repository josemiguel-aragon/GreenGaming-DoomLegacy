# Import libraries
library(ScottKnottESD)
library(readr)
library(ggplot2)

# load data
model_performance <- read_csv("ec_measurements_df.csv")
model_performance <- model_performance[c(3:length(model_performance))]

# apply ScottKnottESD and prepare a ScottKnottESD dataframe
sk_results <- sk_esd(model_performance)
sk_ranks <- data.frame(model = names(sk_results$groups),
        rank = paste0('Rank-', sk_results$groups))

# prepare a dataframe for generating a visualisation
plot_data <- melt(model_performance)
plot_data <- merge(plot_data, sk_ranks, by.x = 'variable', by.y = 'model')

plot_data$variable <- as.character(plot_data$variable)

plot_data$variable[plot_data$variable == 'O1'] <- "-O1"
plot_data$variable[plot_data$variable == 'O2'] <- "-O2"
plot_data$variable[plot_data$variable == 'O3'] <- "-O3"
plot_data$variable[plot_data$variable == 'Os'] <- "-Os"
plot_data$variable[plot_data$variable == 'Oz'] <- "-Oz"


# generate a visualisationz
g <- ggplot(data = plot_data, aes(x = variable, y = value)) +
    geom_boxplot(notch = TRUE, size = 0.25, # Líneas más delgadas
                 outlier.shape = 1, # Forma de círculo hueco para los outliers
                 outlier.size = 2, # Tamaño pequeño de los outliers
                 outlier.stroke = 0.5) +
    stat_boxplot(geom ='errorbar', width = 0.25, size = 0.25) +
    facet_grid(~rank, scales = 'free_x') +
    scale_fill_brewer(direction = -1) +
    ylab('Energy consumption (mWs)') + xlab('') + ggtitle('') + theme_bw() +
    #theme(axis.line = element_line(color = "black", size = 0.5)) +
    theme(axis.title = element_text(size = 41.5, face = "plain")) +
    stat_summary(fun = median, geom = "crossbar", 
               width = 0.5, color = "lightcoral", size = 0.25) +
    theme(text = element_text(size = 48)) +
    theme(panel.grid.major = element_line(color = "grey80", size = 0.0),
           panel.grid.minor = element_line(color = "grey90", size = 0.0)) +
    #theme(panel.border = element_blank()) +
    theme(axis.title.x = element_text(margin = margin(t = 0.01)),
           axis.title.y = element_text(margin = margin(r = 10))) +
    theme(legend.position = 'none')+
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave("ecRankingGenericRaspiPolybench.png")
g


# Import libraries
library(ScottKnottESD)
library(readr)
library(ggplot2)

# load data
model_performance <- read_csv("ec_measurements_df.csv")
model_performance <- model_performance[c(2:length(model_performance))]

# apply ScottKnottESD and prepare a ScottKnottESD dataframe
sk_results <- sk_esd(model_performance)
sk_ranks <- data.frame(model = names(sk_results$groups),
                       rank = paste0('Rank-', sk_results$groups))

# prepare a dataframe for generating a visualisation
plot_data <- melt(model_performance)
plot_data <- merge(plot_data, sk_ranks, by.x = 'variable', by.y = 'model')

plot_data$variable <- as.character(plot_data$variable)

plot_data$variable[plot_data$variable == 'O0'] <- "-O0"
plot_data$variable[plot_data$variable == 'O1'] <- "-O1"
plot_data$variable[plot_data$variable == 'O2'] <- "-O2"
plot_data$variable[plot_data$variable == 'O3'] <- "-O3"
plot_data$variable[plot_data$variable == 'Os'] <- "-Os"
plot_data$variable[plot_data$variable == 'Oz'] <- "-Oz"


# generate a visualisationz
g <- ggplot(data = plot_data, aes(x = variable, y = value)) +
  geom_boxplot(notch = FALSE, size = 0.25, # Líneas más delgadas
               outlier.shape = 1, # Forma de círculo hueco para los outliers
               outlier.size = 2, # Tamaño pequeño de los outliers
               outlier.stroke = 0.5) +
  stat_boxplot(geom ='errorbar', width = 0.25, size = 0.25) +
  facet_grid(~rank, scales = 'free_x') +
  scale_fill_brewer(direction = -1) +
  ylab('Energy Consumption (J)') + xlab('') + ggtitle('') + theme_bw() +
  #theme(axis.line = element_line(color = "black", size = 0.5)) +
  theme(axis.title = element_text(size = 32, face = "plain")) +
  stat_summary(fun = median, geom = "crossbar", 
               width = 0.5, color = "lightcoral", size = 0.25) +
  theme(text = element_text(size = 32)) +
  theme(panel.grid.major = element_line(color = "grey80", size = 0.0),
        panel.grid.minor = element_line(color = "grey90", size = 0.0)) +
  #theme(panel.border = element_blank()) +
  theme(axis.title.x = element_text(margin = margin(t = 0.01)),
        axis.title.y = element_text(margin = margin(r = 10))) +
  theme(legend.position = 'none')+
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave("ecRankingDoomLegacy.png")
g 
  
# Import libraries
library(ScottKnottESD)
library(readr)
library(ggplot2)

# load data
model_performance <- read_csv("memory_measurements_df.csv")
model_performance <- model_performance[c(2:length(model_performance))]

# apply ScottKnottESD and prepare a ScottKnottESD dataframe
sk_results <- sk_esd(model_performance)
sk_ranks <- data.frame(model = names(sk_results$groups),
                       rank = paste0('Rank-', sk_results$groups))

# prepare a dataframe for generating a visualisation
plot_data <- melt(model_performance)
plot_data <- merge(plot_data, sk_ranks, by.x = 'variable', by.y = 'model')

plot_data$variable <- tolower(plot_data$variable)

# generate a visualisation
g <- ggplot(data = plot_data, aes(x = variable, y = value, fill = rank)) +
  geom_boxplot(notch = FALSE) +
  facet_grid(~rank, scales = 'free_x') +
  scale_fill_brewer(direction = -1) +
  ylab('Kbytes') + xlab('Optimization flag') + ggtitle('') + theme_bw() +
  theme(text = element_text(size = 16),
        axis.text.x = element_text(size=6),
        legend.position = 'none')
g
