import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import matplotlib.pylab as pylab
params = {'axes.labelsize': 32,
         'xtick.labelsize': 26,
         'ytick.labelsize': 26}
pylab.rcParams.update(params)


input_files = ["-O0", "ga_doom"]
bench = "doomlegacy"

if __name__ == '__main__':
    labels = ["-O0", "ga_doom"]
    tags = ["-O0", "GA"]
    
    data_power = []
    data_time = []
    data_process = []
    
    df2 = pd.DataFrame()
    
    for i,x in enumerate(input_files):
        count = 0
        print(x)
        #print(f'power_measurements_firefox{x}_cdp.csv')
        data_time.append(np.loadtxt(f'solutions_ec_fitness_{x}_{bench}_large.csv', delimiter=',') / 1000)
        
        
        print(np.median(data_time[-1]))
        
        if i != 0:
            print((np.median(data_time[-1])- np.median(data_time[0]))/np.median(data_time[0]) * 100)
            
        #data_process.append(np.loadtxt(f'size_measurements_firefox{x}_cdp.csv', delimiter=','))
        if "-O" in x:
            df2[x.replace('-','')] = data_time[-1]
        else:
            df2[tags[i]] = data_time[-1]
            
            
    
    df2.to_csv("ec_measurements_df_large.csv")
    
    fig = plt.figure(figsize=(12, 6.5))

    
    plt.plot([i for i in range(1,len(input_files)+1)], np.median(np.array(data_time), axis=1), color='indianred', alpha=0.75, label="_no_legend")
    plt.plot([i for i in range(1,len(input_files)+1)], np.array(data_time).min(axis=1), color='k', linestyle='dashed', linewidth=0.75, alpha=0.75, label='Line of best fit: Runtime Versus Optimization flag')
    plt.plot([i for i in range(1,len(input_files)+1)], np.array(data_time).max(axis=1), color='k', linestyle='dashed', linewidth=0.75, alpha=0.75, label='_no_legend')
    plt.fill_between([i for i in range(1,len(input_files)+1)], np.array(data_time).min(axis=1), np.array(data_time).max(axis=1), color='mediumseagreen', alpha=0.25, label="Range of Min and Max Runtime per Optimization flag")
    bp = plt.boxplot(data_time, labels=tags, patch_artist=True)
    for patch in bp['boxes']:
        patch.set(facecolor='w')
    plt.ylabel("Energy consumptions (J)")
    fig.tight_layout(pad=1.5)

    plt.savefig("./improvementbpDoomLegacy-ec-large.png", dpi=300)    