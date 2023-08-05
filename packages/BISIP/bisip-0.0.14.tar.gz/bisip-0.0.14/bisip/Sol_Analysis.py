#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 14:00:58 2017

@author: Charles
"""
from __future__ import division
from __future__ import print_function

from builtins import zip
from builtins import range
from past.builtins import basestring
from past.utils import old_div
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
from scipy.stats import norm, gaussian_kde
#import cPickle as pickle

sym_labels = dict([('resi', r"$\rho\/(\Omega\cdot m)$"),
                   ('freq', r"Frequency $(Hz)$"),
                   ('phas', r"-Phase (mrad)"),
                   ('ampl', r"$|\rho|$ (normalized)"),
                   ('real', r"$\rho$' (normalized)"),
                   ('imag', r"$-\rho$'' (normalized)")])


def load_object(filename):
    with open(filename, 'rb') as input:
        obj = pickle.load(input)
    return obj

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

#adapt = True
noise = 1
adapt = False
filename = "%dmrad_PDecomp_1_MCMC_Solutions_Adaptive_%s.pkl"%(noise,adapt)
#sol = load_object(filename)

if adapt:
    title = "Adaptive Metropolis"
else:
    title = "Metropolis-Hastings"



def plot_histo(sol, no_subplots=False, save=False, save_as_png=True):
    MDL = sol["pymc_model"]
    filename = sol["path"].replace("\\", "/").split("/")[-1].split(".")[0]
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    try:
        keys.remove("zmod")
        keys.remove("m_")
    except:
        pass
#    keys.remove("R0")
    for (i, k) in enumerate(keys):
        vect = old_div((MDL.trace(k)[:].size),(len(MDL.trace(k)[:])))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(0,vect)]
    keys = list(flatten(keys))
#    labels = [r"$c_1$", "$c_2$", r"$log_{10}\/\tau_1$", r"$log_{10}\/\tau_2$", "$m_1$", "$m_2$"]
    labels = [r"$log_{10}\bar{\tau}$", "$\Sigma m$", "$R_0$", "$a_0$", "$a_1$", "$a_2$", "$a_3$", "$a_4$"]
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(10, nrows*2.2))
    for c, (a, k) in enumerate(zip(ax.flat, keys)):
        if k == "R0":
            stoc = "R0"
        else:
            stoc =  ''.join([i for i in k if not i.isdigit()])
            stoc_num = [int(i) for i in k if i.isdigit()]        
        try:          
            maxi = np.argmax(MDL.trace("log_tau")[-1])
            mini = np.argmin(MDL.trace("log_tau")[-1])
            if stoc_num[0] == 0:
                data = MDL.trace(stoc)[:][:,maxi]
                #prendre plus petit
            elif stoc_num[0] == 1:
                #prendre plus gros
                data = MDL.trace(stoc)[:][:,mini]
#            else:
#                #prendre plus moyen
#                remaining = [x for x in range(0,vect) if x != mini and x != maxi][0]
#                data = MDL.trace(stoc)[:][:,remaining]
        except:
            pass
        try:
            data = MDL.trace(stoc)[:][:,stoc_num[0]-1]
        except:
            data = MDL.trace(stoc)[:]
        fit = norm.pdf(sorted(data), np.mean(data), np.std(data))
        print((np.mean(data), np.std(data)))
        plt.axes(a)
#            plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
#            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        plt.locator_params(axis = 'y', nbins = 7)
        plt.locator_params(axis = 'x', nbins = 7)
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14)
        plt.xlabel(labels[c], fontsize=14)
        plt.ylabel("Frequency", fontsize=14)
        ty = a.yaxis.get_offset_text()
        ty.set_size(12)
        tx = a.xaxis.get_offset_text()
        tx.set_size(12)
        hist = plt.hist(data, bins=20, normed=False, label=filename, linewidth=1.0, color="white")
        xh = [0.5 * (hist[1][r] + hist[1][r+1]) for r in range(len(hist[1])-1)]
        binwidth = old_div((max(xh) - min(xh)), len(hist[1]))
        fit *= len(data) * binwidth
        plt.plot(sorted(data), fit, "-b", linewidth=1.5)
        plt.grid(None)
        plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    fig.tight_layout(w_pad=0, h_pad=0)
    return fig





def plot_errors(sol, ax, noise):
    MDL = sol["pymc_model"]
#    model = get_model_type(sol)
    filename = sol["path"].replace("\\", "/").split("/")[-1].split(".")[0]
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    sampler = MDL.get_state()["sampler"]
    try:
        keys.remove("zmod")
        keys.remove("m_")
    except:
        pass
    for (i, k) in enumerate(keys):
        vect = old_div((MDL.trace(k)[:].size),(len(MDL.trace(k)[:])))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(0,vect)]
    keys = list(flatten(keys))
    labels = [r"$log_{10}\bar{\tau}$", "$\Sigma m$", "$R_0$", "$a_0$", "$a_1$", "$a_2$", "$a_3$", "$a_4$"]
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    for c, (a, k) in enumerate(zip(ax.flat, keys)):
        if k == "R0":
            stoc = "R0"
        else:
            stoc =  ''.join([i for i in k if not i.isdigit()])
            stoc_num = [int(i) for i in k if i.isdigit()]
        try:
            mean = np.mean(MDL.trace(stoc)[:][:,stoc_num[0]-1])
            SD = np.std(MDL.trace(stoc)[:][:,stoc_num[0]-1])
        except:
            mean = np.mean(MDL.trace(stoc)[:])
            SD = np.std(MDL.trace(stoc)[:])

#        x = np.arange(sampler["_burn"]+1, sampler["_iter"]+1, sampler["_thin"])
        plt.axes(a)
        a.grid(False)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,2))
        plt.locator_params(axis = 'y', nbins = 6)
        plt.yticks(fontsize=14)
        plt.xticks(list(range(0,12)),["","1","2","3","4","5","6","7","8","9","10"], fontsize=14)
        plt.ylabel(labels[c], fontsize=14)
        ty = a.yaxis.get_offset_text()
        ty.set_size(12)
        tx = a.xaxis.get_offset_text()
        tx.set_size(12)        
        plt.xlim([0.5, 10.5])
        plt.errorbar(noise+1, mean, SD, None, 'ob', label=filename, linewidth=1.0)
#        plt.xticks()

def plot_traces(sol, ax, color="b"):
    MDL = sol.MDL
#    model = get_model_type(sol)
    filename = sol.filename.replace("\\", "/").split("/")[-1].split(".")[0]
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    sampler = MDL.get_state()["sampler"]
    try:
        keys.remove("zmod")
        keys.remove("m_")
    except:
        pass
    keys.remove("R0")
    for (i, k) in enumerate(keys):
        vect = old_div((MDL.trace(k)[:].size),(len(MDL.trace(k)[:])))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(0,int(vect))]
    labels = [r"$log_{10}\bar{\tau}$", "$\Sigma m$", "$R_0$", "$a_0$", "$a_1$", "$a_2$", "$a_3$", "$a_4$"]
#    labels = [r"$R_0$", "$c_1$", "$c_2$", "$c_3$", r"$log_{10}\/\tau_1$", r"$log_{10}\/\tau_2$", r"$log_{10}\/\tau_3$", "$m_1$", "$m_2$", "$m_3$"]
#    labels = [r"$c_1$", "$c_2$", r"$log_{10}\/\tau_1$", r"$log_{10}\/\tau_2$", "$m_1$", "$m_2$"]
    keys = list(flatten(keys))
    ncols = 2
    nrows = int(ceil(len(keys)*1.0 / ncols))
    for c, (a, k) in enumerate(zip(ax.flat, keys)):
        if k == "R0":
            stoc = "R0"
        else:
            stoc =  ''.join([i for i in k if not i.isdigit()])
            stoc_num = [int(i) for i in k if i.isdigit()]        
        try:          
            maxi = np.argmax(MDL.trace("log_tau")[-1])
            mini = np.argmin(MDL.trace("log_tau")[-1])
            if stoc_num[0] == 0:
                data = MDL.trace(stoc)[:][:,maxi]
                #prendre plus petit
            elif stoc_num[0] == 1:
                #prendre plus gros
                data = MDL.trace(stoc)[:][:,mini]
#            else:
#                #prendre plus moyen
#                remaining = [x for x in range(0,vect) if x != mini and x != maxi][0]
#                data = MDL.trace(stoc)[:][:,remaining]
#        except:
#            pass
#        try:
#            data = MDL.trace(stoc)[:][:,stoc_num[0]-1]
        except:
            data = MDL.trace(stoc)[:]
            
        print((np.mean(data[-100000:]), np.std(data[-100000:])))
            
        x = np.arange(sampler["_burn"]+1, sampler["_iter"]+1, sampler["_thin"])
        plt.axes(a)
        plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
        plt.locator_params(axis = 'x', nbins = 3)
        ty = a.yaxis.get_offset_text()
        ty.set_size(12)
        tx = a.xaxis.get_offset_text()
        tx.set_size(12)
        plt.locator_params(axis = 'y', nbins = 6)
        plt.yticks(fontsize=14)
        plt.xticks(fontsize=14)
        plt.ylabel(labels[c], fontsize=14)
        plt.plot(x, data, '-', color=color, label=filename, linewidth=1.0)
        a.grid(False)


def plot_debye(s, ax):
    x = np.log10(s["data"]["tau"])
    x = np.linspace(min(x), max(x),100)
    

    y = 100*np.sum([a*(x**i) for (i, a) in enumerate(s["params"]["a"])], axis=0)
#    ax.errorbar(10**x[(x>-6)&(x<2)], y[(x>-6)&(x<2)], None, None, "-", color='lightgray',linewidth=1, label="RTD estimations (%d)"%len(sol))
    ax.set_xlabel("Relaxation time (s)", fontsize=14)
    ax.set_ylabel("Chargeability (%)", fontsize=14)
    plt.yticks(fontsize=14), plt.xticks(fontsize=14)
    plt.xscale("log")
    ax.set_xlim([1e-6, 1e1])
    ax.set_ylim([0, 5.0])

def plot_mean_debye(sol, ax):
    x = np.log10(sol[0]["data"]["tau"])
    x = np.linspace(min(x), max(x),100)
    list_best_rtd = [100*np.sum([a*(x**i) for (i, a) in enumerate(s["params"]["a"])], axis=0) for s in sol]
#    list_best_rtd = [s["fit"]["best"] for s in sol]
    y = np.mean(list_best_rtd, axis=0)
    y_min = 100*np.sum([a*(x**i) for (i, a) in enumerate(sol[0]["params"]["a"] - sol[0]["params"]["a_std"])], axis=0)
    y_max = 100*np.sum([a*(x**i) for (i, a) in enumerate(sol[0]["params"]["a"] + sol[0]["params"]["a_std"])], axis=0)
    ax.errorbar(10**x[(x>-6)&(x<2)], y[(x>-6)&(x<2)], None, None, "-", color='blue',linewidth=2, label="Mean RTD", zorder=10)
    plt.plot(10**x[(x>-6)&(x<2)], y_min[(x>-6)&(x<2)], color='lightgray', alpha=1, zorder=-1, label="RTD range")
    plt.plot(10**x[(x>-6)&(x<2)], y_max[(x>-6)&(x<2)], color='lightgray', alpha=1, zorder=-1)
    plt.fill_between(sol[0]["data"]["tau"], 100*(sol[0]["params"]["m_"]-sol[0]["params"]["m__std"])  , 100*(sol[0]["params"]["m_"]+sol[0]["params"]["m__std"]), color='lightgray', alpha=1, zorder=-1, label="RTD SD")
    
    ax.set_xlabel("Relaxation time (s)", fontsize=14)
    ax.set_ylabel("Chargeability (%)", fontsize=14)
    plt.yticks(fontsize=14), plt.xticks(fontsize=14)
    plt.xscale("log")
    ax.set_xlim([1e-6, 1e1])
    ax.set_ylim([0, 5.0])
    ax.legend(loc=1, fontsize=12)
#    ax.set_title(title+" step method", fontsize=14)

def plot_data(sol, ax):
    data = sol["data"]
    f = data["freq"]
    Zr0 = max(abs(data["Z"]))
    zn_dat = old_div(data["Z"],Zr0)
    zn_err = old_div(data["Z_err"],Zr0)
    # Real-Imag
    plt.axes(ax[1])
#    plt.errorbar(f, -zn_dat.imag, zn_err.imag, None, '.b', label='Synthetic data\n(%d mrad noise)'%noise,zorder=2)
    plt.errorbar(f, -zn_dat.imag, zn_err.imag, None, '.b', label='Laboratory data',zorder=2)
    plt.axes(ax[0])
    plt.errorbar(f, zn_dat.real, zn_err.real, None, '.b', label='Laboratory data',zorder=2)

def plot_mean_fit(sol, ax):
    data = sol[0]["data"]
    Zr0 = max(abs(data["Z"]))
    f = data["freq"]
    list_best_fit = [s["fit"]["best"] for s in sol]
    mean_fit = old_div(np.mean(list_best_fit, axis=0),Zr0)
    # Real-Imag
    plt.axes(ax[1])
    plt.semilogx(f, -mean_fit.imag, '-r', linewidth=2, label='Mean fit', zorder=1)
    plt.legend(loc=2, fontsize=12)
    plt.axes(ax[0])
    plt.semilogx(f, mean_fit.real, '-r',linewidth=2, label='Mean fit', zorder=1)
    plt.legend(loc=3, fontsize=12)

def plot_fit(s, ax):
    filepath = s["path"]
    sample_name = filepath.replace("\\", "/").split("/")[-1].split(".")[0]
    data = s["data"]
    fit = s["fit"]
    # Graphiques du fit
    f = data["freq"]
    Zr0 = max(abs(data["Z"]))
    zn_dat = old_div(data["Z"],Zr0)
    zn_err = old_div(data["Z_err"],Zr0)
    zn_fit = old_div(fit["best"],Zr0)
    zn_min = old_div(fit["lo95"],Zr0)
    zn_max = old_div(fit["up95"],Zr0)
#    for t in ax:
#        t.tick_params(labelsize=14)
    # Real-Imag
    plt.axes(ax[1])
    plt.semilogx(f, -zn_fit.imag, '-', color='lightgray', zorder=0, label="Fitted models (%d)"%len(sol))
    plt.fill_between(f, -zn_max.imag, -zn_min.imag, color='lightgray', alpha=1, zorder=-1)
    plt.xlabel(sym_labels['freq'], fontsize=14)
    plt.ylabel(sym_labels['imag'], fontsize=14)
#    plt.legend(loc=2, numpoints=1, fontsize=14)
#        plt.xlim([None, 1])
#    plt.title(title+" step method", fontsize=14)
    plt.ylim([0, max(-zn_dat.imag)])
    # Freq-Ampl
#        plt.axes(ax[0])
#        plt.errorbar(f, Amp_dat, Amp_err, None, '.', label='Data')
#        plt.semilogx(f, Amp_fit, 'r-', label='Fitted model')
#        plt.fill_between(f, Amp_max, Amp_min, color='dimgray', alpha=0.3)
#        plt.xlabel(sym_labels['freq'], fontsize=14)
#        plt.ylabel(sym_labels['ampl'], fontsize=14)
#        ax[0].legend(loc=1, numpoints=1, fontsize=12)
#        plt.ylim([None,1.0])

#    # Freq-Phas
#    # Real-Imag
    plt.axes(ax[0])
    plt.semilogx(f, zn_fit.real, '-', color='lightgray',zorder=0, label="Fitted models (%d)"%len(sol))
    plt.fill_between(f, zn_min.real, zn_max.real, color='lightgray', alpha=1, zorder=-1)
    plt.xlabel(sym_labels['freq'], fontsize=14)
    plt.ylabel(sym_labels['real'], fontsize=14)
#    plt.legend([handle_dat, handle_fit], ["Data", "Fitted models"], loc=1, numpoints=1, fontsize=14)
#    plt.xlim([None, 1])
    plt.ylim([0.0, 1.0])
#    
    #        plt.title(sample_name, fontsize=12)
#    plt.subplots_adjust(top=0.55)
#    plt.title(title+" step method", fontsize=14)

def plot_all_chains_KDE(sol):
#    MDL = sol["pymc_model"]
    
    MDLs = [m["pymc_model"] for m in sol]
    
#    model = get_model_type(sol)
    keys = sorted([x.__name__ for x in MDLs[0].deterministics]) + sorted([x.__name__ for x in MDLs[0].stochastics])
    sampler = MDLs[0].get_state()["sampler"]
    
    last_iter = sampler["_iter"] - sampler["_burn"]
    
    try:
        keys.remove("zmod")
        keys.remove("m_")
#        keys.remove("log_mean_tau")
#        keys.remove("total_m")
    except:
        pass
    for (i, k) in enumerate(keys):
        vect = old_div((MDLs[0].trace(k)[:].size),(len(MDLs[0].trace(k)[:])))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(0,vect)]
    keys = list(flatten(keys))
    ncols = len(keys)
    nrows = len(keys)    
#    labels = [r"$R_0$", "$c_1$", "$c_2$", "$c_3$", r"$log_{10}\/\tau_1$", r"$log_{10}\/\tau_2$", r"$log_{10}\/\tau_3$", "$m_1$", "$m_2$", "$m_3$"]
    labels = [r"$R_0$", "$c_1$", "$c_2$", r"$log_{10}\/\tau_1$", r"$log_{10}\/\tau_2$", "$m_1$", "$m_2$"]

    fig = plt.figure(figsize=(9,9))
#    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    plotz = len(keys)    
    for i in range(plotz):
        for j in range(plotz):
            if j<i:
                var1 = keys[j]
                var2 = keys[i]
                label1 = labels[j]
                label2 = labels[i]
                
                print((label1, label2))
                ax = plt.subplot2grid((plotz-1, plotz-1), (i-1,j))
                ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,0))
                ax.ticklabel_format(axis='x', style='sci', scilimits=(-2,0))
                if var1 == "R0":
                    stoc1 = "R0"
                else:
                    stoc1 =  ''.join([k for k in var1 if not k.isdigit()])
                    stoc_num1 = [int(k) for k in var1 if k.isdigit()]
                
                x = np.array([])
                try:
                    for mod in MDLs:
                        maxi = np.argmax(mod.trace("log_tau")[-1])
                        mini = np.argmin(mod.trace("log_tau")[-1])
                        if stoc_num1[0] == 0:
                            data1 = mod.trace(stoc1)[:][:,maxi]
                            #prendre plus petit
                        elif stoc_num1[0] == 1:
                            #prendre plus gros
                            data1 = mod.trace(stoc1)[:][:,mini]
#                        else:
#                            #prendre plus moyen
#                            remaining = [re for re in range(0,vect) if re != mini and re != maxi][0]
#                            data1 = mod.trace(stoc1)[:][:,remaining]
                        x = np.hstack((x,data1))
                except:
                    for mod in MDLs:
                        x = np.hstack((x,mod.trace(stoc1)[:]))
                        
                if var2 == "R0":
                    stoc2 = "R0"
                else:
                    stoc2 =  ''.join([k for k in var2 if not k.isdigit()])
                    stoc_num2 = [int(k) for k in var2 if k.isdigit()]
                
                y = np.array([])
                try:
                    for mod in MDLs:
                        maxi = np.argmax(mod.trace("log_tau")[-1])
                        mini = np.argmin(mod.trace("log_tau")[-1])
                        if stoc_num2[0] == 0:
                            data2 = mod.trace(stoc2)[:][:,maxi]
                            #prendre plus petit
                        elif stoc_num2[0] == 1:
                            #prendre plus gros
                            data2 = mod.trace(stoc2)[:][:,mini]
#                        else:
#                            #prendre plus moyen
#                            remaining = [re for re in range(0,vect) if re != mini and re != maxi][0]
#                            data2 = mod.trace(stoc2)[:][:,remaining]
                        y = np.hstack((y,data2))
                except:
                    for mod in MDLs:
                        y = np.hstack((y,mod.trace(stoc2)[:]))
                
                xmin, xmax = min(x), max(x)
                ymin, ymax = min(y), max(y) 
                # Peform the kernel density estimate
                xx, yy = np.mgrid[xmin:xmax:50j, ymin:ymax:50j]
                positions = np.vstack([xx.ravel(), yy.ravel()])
                values = np.vstack([x, y])
                kernel = gaussian_kde(values)
                kernel.set_bandwidth(bw_method='silverman')
                kernel.set_bandwidth(bw_method=kernel.factor * 1.0)
                f = np.reshape(kernel(positions).T, xx.shape)
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                plt.axes(ax)
                # Contourf plot
                plt.grid(None)
                ax.scatter(x, y, color='k', s=1)
#                plt.title("           r = %.2f"%(np.corrcoef(x,y)[0,1]), fontsize=14)
                plt.title("r = %.2f"%(np.corrcoef(x,y)[0,1]), fontsize=14)
                plt.xticks(rotation=90)
                plt.locator_params(axis = 'y', nbins = 6)
                plt.locator_params(axis = 'x', nbins = 6)
                cfset = ax.contourf(xx, yy, f, cmap=plt.cm.Blues, alpha=0.7)
                ## Or kernel density estimate plot instead of the contourf plot
                # Contour plot
#                cset = ax.contour(xx, yy, f, levels=cfset.levels[2::2], colors='k', alpha=0.8)
                # Label plot
            #    ax.clabel(cset, cset.levels[::1], inline=1, fmt='%.1E', fontsize=10)
                plt.yticks(fontsize=14)
                plt.xticks(fontsize=14)
                if j == 0:
                    plt.ylabel("%s" %label2, fontsize=14)
                if i == len(keys)-1:
                    plt.xlabel("%s" %label1, fontsize=14)
                if j != 0:
                    ax.yaxis.set_ticklabels([])
                if i != len(keys)-1:
                    ax.xaxis.set_ticklabels([])
                    
                ty = ax.yaxis.get_offset_text()
                ty.set_size(12)
                tx = ax.xaxis.get_offset_text()
                tx.set_size(12)
                            
                plt.suptitle("Double Cole-Cole inversion\n"+title+" step method", fontsize=14)

    fig.tight_layout(pad=0, w_pad=1, h_pad=0) 
    fig.savefig('KDE_ColeCole-3_Matrix_Adaptive_False.png', dpi=300)

    return fig


def plot_all_KDE(sol):
    MDL = sol["pymc_model"]
#    model = get_model_type(sol)
    filename = sol["path"].replace("\\", "/").split("/")[-1].split(".")[0]
    keys = sorted([x.__name__ for x in MDL.deterministics]) + sorted([x.__name__ for x in MDL.stochastics])
    sampler = MDL.get_state()["sampler"]
    try:
        keys.remove("zmod")
        keys.remove("m_")
#        keys.remove("log_mean_tau")
#        keys.remove("total_m")
    except:
        pass
    for (i, k) in enumerate(keys):
        vect = old_div((MDL.trace(k)[:].size),(len(MDL.trace(k)[:])))
        if vect > 1:
            keys[i] = [k+"%d"%n for n in range(0,vect)]
    keys = list(flatten(keys))
    ncols = len(keys)
    nrows = len(keys)    
    labels = [r"$log_{10}\bar{\tau}$", "$\Sigma m$", "$R_0$", "$a_0$", "$a_1$", "$a_2$", "$a_3$", "$a_4$"]
    fig = plt.figure(figsize=(13,13))
#    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    plotz = len(keys)    
    for i in range(plotz):
        for j in range(plotz):
            if j<i:
                var1 = keys[j]
                var2 = keys[i]
                label1 = labels[j]
                label2 = labels[i]
                
                print((label1, label2))
                ax = plt.subplot2grid((plotz-1, plotz-1), (i-1,j))
                ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,0))
                ax.ticklabel_format(axis='x', style='sci', scilimits=(-2,0))
                if var1 == "R0":
                    stoc1 = "R0"
                else:
                    stoc1 =  ''.join([k for k in var1 if not k.isdigit()])
                    stoc_num1 = [int(k) for k in var1 if k.isdigit()]
                try:
                    x = MDL.trace(stoc1)[:,stoc_num1[0]-1]
                except:
                    x = MDL.trace(stoc1)[:]
                if var2 == "R0":
                    stoc2 = "R0"
                else:
                    stoc2 =  ''.join([k for k in var2 if not k.isdigit()])
                    stoc_num2 = [int(k) for k in var2 if k.isdigit()]
                try:
                    y = MDL.trace(stoc2)[:,stoc_num2[0]-1]
                except:
                    y = MDL.trace(stoc2)[:]
                    
#                y = all_chains
                    
                xmin, xmax = min(x), max(x)
                ymin, ymax = min(y), max(y) 
                # Peform the kernel density estimate
                xx, yy = np.mgrid[xmin:xmax:50j, ymin:ymax:50j]
                positions = np.vstack([xx.ravel(), yy.ravel()])
                values = np.vstack([x, y])
                kernel = gaussian_kde(values)
                kernel.set_bandwidth(bw_method='silverman')
                kernel.set_bandwidth(bw_method=kernel.factor * 2.)
                f = np.reshape(kernel(positions).T, xx.shape)
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                plt.axes(ax)
                # Contourf plot
                plt.grid(None)
                ax.scatter(x, y, color='k', s=1)
                plt.title("           r = %.2f"%(np.corrcoef(x,y)[0,1]), fontsize=14)
                plt.xticks(rotation=90)
                plt.locator_params(axis = 'y', nbins = 6)
                plt.locator_params(axis = 'x', nbins = 6)
                cfset = ax.contourf(xx, yy, f, cmap=plt.cm.Blues, alpha=0.7)
                ## Or kernel density estimate plot instead of the contourf plot
                # Contour plot
#                cset = ax.contour(xx, yy, f, levels=cfset.levels[2::2], colors='k', alpha=0.8)
                # Label plot
            #    ax.clabel(cset, cset.levels[::1], inline=1, fmt='%.1E', fontsize=10)
                plt.yticks(fontsize=14)
                plt.xticks(fontsize=14)
                if j == 0:
                    plt.ylabel("%s" %label2, fontsize=14)
                if i == len(keys)-1:
                    plt.xlabel("%s" %label1, fontsize=14)
                if j != 0:
                    ax.yaxis.set_ticklabels([])
                if i != len(keys)-1:
                    ax.xaxis.set_ticklabels([])
                    
                ty = ax.yaxis.get_offset_text()
                ty.set_size(12)
                tx = ax.xaxis.get_offset_text()
                tx.set_size(12)
                            
                plt.suptitle(title+" step method", fontsize=14)

    fig.tight_layout(pad=0, w_pad=0.0, h_pad=0) 
    fig.savefig('KDE_Warburg_Matrix_Adaptive_%s.png'%(adapt), dpi=300)
    return fig

def compare_fits():
    fig, ax = plt.subplots(1, 2, figsize=(10,4))
    plot_data(sol[0], ax)
    plot_fit(sol[0], ax)
    plot_mean_fit(sol, ax)
    for s in sol:
        plot_fit(s, ax)
#    ax[0].set_title("Model 4 ($c_1 = 0.4$, $m_1 = 0.4$)")
#    ax[1].set_title("Model 4 ($c_1 = 0.4$, $m_1 = 0.4$)")
    ax[0].set_title("Sample B")
    ax[1].set_title("Sample B")
    ax[0].set_ylim([0,1.1])
    ax[1].set_ylim([-0.01,None])
    fig.tight_layout()
#    fig.savefig('%d_Attempts_Adaptive_%s'%(len(sol), adapt))
#    fig.savefig('%d_Attempts-SampleB_ColeCole_Adaptive_False'%(len(sol)))


def compare_fits_RTD():
    fig, ax = plt.subplots(1, 2, figsize=(10,4))
    
#    plot_debye(sol[0], ax[1])
    plot_mean_debye(sol, ax[1])
    for s in sol:
        plot_debye(s, ax[1])
    plot_data(sol[0], ax)
    plot_fit(sol[0], ax)
    plot_mean_fit(sol, ax)
    for s in sol:
        plot_fit(s, ax)
    ax[1].set_title("Sample B")
    fig.tight_layout()
    fig.savefig('WARBURGLAB_SampleB_Noise_%dmrad_%d_Attempts_FIT_RTD_Adaptive_%s'%(noise,len(sol), adapt))

def compare_errors():
    fig, ax = plt.subplots(4, 2, figsize=(10,4*2))
#    ax[0,0].set_title(title+" step method", fontsize=14)
    for c, s in enumerate(sol):
        plot_errors(s, ax, c)
    ax[3,0].set_xlabel("Measurement noise (mrad)", fontsize=14)
    ax[3,1].set_xlabel("Measurement noise (mrad)", fontsize=14)
    fig.tight_layout(pad=0, w_pad=1, h_pad=0.5)
    fig.savefig('%d_Errors_Adaptive_%s'%(len(sol), adapt), dpi=300)
        
def compare_RTD():
    fig, ax = plt.subplots(figsize=(5,4))
    plot_debye(sol[0], ax)
    plot_mean_debye(sol, ax)
    for s in sol:
        plot_debye(s, ax)
    plt.title(title+" step method", fontsize=14)
    fig.tight_layout()
    fig.savefig('%d_RTD_Adaptive_%s'%(len(sol), adapt))

def compare_traces():
#    fig, ax = plt.subplots(2, 1, figsize=(6,4)) # Debye
    fig, ax = plt.subplots(4, 2, figsize=(10,4*2)) # Debye
#    fig, ax = plt.subplots(5, 2, figsize=(10,4*2)) # ColeCole
#    ax[0,0].set_title(title+" step method", fontsize=14)
#    for s, c in zip(sol, ["gray", "blue", "red"]):
    for s in sol:
#        plot_traces(s, ax, color=c)
        plot_traces(s, ax)
#    ax[0,0].set_ylim([-3,0])
#    ax[0,1].set_ylim([0.0,0.4])
#    ax[1,0].set_ylim([0.8,1.3])
#    ax[1,1].set_ylim([-1e-3,2e-3])
#    ax[2,0].set_ylim([-2e-2,5e-2])
#    ax[2,1].set_ylim([-5e-2,5e-2])
#    ax[3,0].set_ylim([-1e-2,1e-2])
#    ax[3,1].set_ylim([-1e-2,1.5e-2])


#    ax[0].set_ylim([-2.,2])
#    ax[1].set_ylim([0,0.1])
#    ax[0].legend(["Sample A"])
#    ax[1].legend(["Sample A"])


#    ax[0,0].set_ylim([0.8,1.3])
#    ax[0,1].set_ylim([0,1])
#    ax[1,0].set_ylim([0,1])
#    ax[1,1].set_ylim([0,1])
#    ax[2,0].set_ylim([-7,4])
#    ax[2,1].set_ylim([-7,4])
#    ax[3,0].set_ylim([-7,4])
#    ax[3,1].set_ylim([0,1])
#    ax[4,0].set_ylim([0,1])
#    ax[4,1].set_ylim([0,1])

#    ax[0].xaxis.set_ticklabels([])
#    ax[1].xaxis.set_ticklabels([])
#    ax[0,1].xaxis.set_ticklabels([])
#    ax[1,0].xaxis.set_ticklabels([])
#    ax[1,1].xaxis.set_ticklabels([])

#    ax[0].set_title("Warburg decomposition")

#    ax[-1].set_xlabel("Iteration number", fontsize=14)        
#    ax[-1,-1].set_xlabel("Iteration number", fontsize=14)  
    fig.tight_layout(pad=0, w_pad=0, h_pad=0.0)
    fig.savefig("10WarburgTracesSampleA.pdf")
#    fig.savefig('%d_Noise_Comp_Traces_Adaptive_%s.pdf'%(len(sol), adapt), dpi=300)
#    fig.savefig('%d_COLECOLE_Comp_Traces_Adaptive_%s.png'%(len(sol), adapt), dpi=300)
#    fig.savefig('%d_doubleCOLECOLE-3_Comp_Traces_Adaptive_%s.png'%(len(sol), adapt), dpi=300)
    