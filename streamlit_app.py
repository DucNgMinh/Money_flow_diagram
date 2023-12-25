import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

from vnstock import *

from calculate import *
from graph import *

import datetime
# Title
st.title("Efficient Portfolio Frontier")
st.write("Github repo: [link](https://github.com/DucNgMinh/Efficient_Frontier_with_streamlit/tree/main)")

# Input date
start = st.date_input('Set an start date for', datetime.date(2021, 1, 1))
st.write('Start is set for', start)

end = st.date_input('Set an end date for', datetime.date(2022, 12, 31))
st.write('End is set for', end)

start = start.strftime("%Y-%m-%d")
end = end.strftime("%Y-%m-%d")

# ticker_list
ticker_list = pd.read_csv(r"listing_companies_enhanced-2023.csv")

# input widget to choose stock option
tickers = st.multiselect("Select two or more stocks:", ticker_list['ticker'])

st.markdown("# Price trend ")
if len(tickers) != 0:
# create price df
        prices_df = calculate_prices_df(tickers, start, end)
        st.pyplot(stock_price_trend_graph(prices_df, start_date= start, end_date= end))
else:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock option to make futher calculations </h3>", unsafe_allow_html=True)

st.markdown("# Log Returns ")
st.markdown("Compute the log return as follows: ")
st.latex(r'''\log r_t = \log \frac{p_t}{p_{t-1}}''')

# create daily returns df
try:
        returns_df = calculate_returns_df(prices_df)
        st.pyplot(daily_returns_stock(returns_df))
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to returns graph </h3>", unsafe_allow_html=True)
    

st.markdown("# Sharpe ratio")
st.markdown("The Sharpe ratio is defined as:")
st.latex(r'''SR(W) = \frac{R(W) - R_f}{\sigma(W)}''')
st.latex("W^T 1 = 1 ")

st.markdown("Since we will look for max $SR(W)$ and $R_f$ is common for all $w's$, then we shall compute:")
st.latex("R(W) = W^T log(r)")
st.latex("\sigma(W) = \sqrt{W^T \Sigma W}")
st.latex(r'''SR(W) ~ \frac{W^T log(r) - R_f}{\sqrt{W^T \Sigma W}}''')

st.markdown("# Simulation of a Stock Portfolio")
n_portfolios = st.number_input('Insert number of simulated portfolio:', value = 1000, step= 1)
risk_free_rate = st.number_input('Insert risk free rate (Percentage):', value = 0.025, step=0.001, format="%0.3f")

try:
        n_stocks = len(tickers)             # number of stock
        # n_portfolios                      # number of simulated portfolio
        mean_returns = returns_df.mean()    # mean return of stock index
        cov_matrix = returns_df.cov()       # covariance matrix
        # risk_free_rate = 0.025            # assumed risk free rate

        # Simulated portfolios
        result_table, weight, expected_Return, expected_Volatility, sharpe_Ratio = simulated_portfolios(n_portfolios, n_stocks, mean_returns, cov_matrix, risk_free_rate)

        # calculate max sharpe allocation
        max_sharpe_index = np.argmax(result_table['Sharpe_Ratio'])
        max_sharpe_allocation = pd.DataFrame(weight[max_sharpe_index],index=returns_df.columns, columns=['allocation'])
        max_sharpe_allocation.allocation = [round(i*100, 2)for i in max_sharpe_allocation.allocation]
        max_sharpe_allocation = max_sharpe_allocation.T


        st.markdown("## Maximum Sharpe Ratio Portfolio Allocation (Percentage)")
        st.write(max_sharpe_allocation)

        # calculate min vol allocation
        min_volality_index = np.argmin(result_table['Volatility'])
        min_vol_allocation = pd.DataFrame(weight[min_volality_index],index=returns_df.columns,columns=['allocation'])
        min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
        min_vol_allocation = min_vol_allocation.T

        st.markdown("## Minimum Volatility Portfolio Allocation (Percentage)")
        st.write(min_vol_allocation)
        st.pyplot(simulated_portfolio_graph(expected_Return, expected_Volatility, max_sharpe_index, min_volality_index, sharpe_Ratio ))
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to draw graph </h3>", unsafe_allow_html=True)

st.markdown("# Portfolio Optimization theory")
st.markdown("The plot of the randomly simulated portfolio exhibits an arch-shaped line positioned above a cluster of blue dots, which is commonly referred to as the efficient frontier. \
                This line is deemed 'efficient' as it represents the portfolio combinations that yield the lowest risk for a given target return.\
                Any points located on the efficient frontier offer the optimal trade-off between risk and return.")
st.markdown("The way we found the two kinds of optimal portfolio above was by simulating many possible random choices and pick the best ones (either minimum risk or maximum risk-adjusted return).")

st.markdown("## Maximum Sharpe ratio portfolio (MSRP)")
st.latex(r'''\begin{aligned}
        & \underset{w}{\text{maximize}}
        & & SR(W) = \frac{R(W) - R_f}{\sigma(W)}\\
        & \text{subject to}
        & &  W^T 1 = 1 \\
        & && W \geq 0 \\
        \end{aligned}''')
st.markdown("However, this problem is not convex so we rewrite in convex form as")
st.latex(r'''\begin{aligned}
        & \underset{w}{\text{minimize}}
        & & -SR(W)\\
        & \text{subject to}
        & &  W^T 1 = 1 \\
        & && W \geq 0 \\
        \end{aligned}''')

try:
        # calculate weight of max sharpe portfolio
        w_opt_sharpe = calculate_max_sharpe_opt_allocation(n_stocks, mean_returns, cov_matrix, risk_free_rate)
        max_sharpe_opt_allocation = pd.DataFrame(w_opt_sharpe['x'], index=returns_df.columns, columns=['allocation'])
        max_sharpe_opt_allocation.allocation = [round(i*100,2)for i in max_sharpe_opt_allocation.allocation]
        max_sharpe_opt_Return, max_sharpe_opt_Volatility, max_sharpe_opt_sharpe_Ratio = calculate(w_opt_sharpe['x'], mean_returns, cov_matrix, risk_free_rate)
        max_sharpe_opt_allocation = max_sharpe_opt_allocation.T
        # display
        st.write("Maximum Sharpe Ratio Optimal Portfolio Allocation (Percentage)")
        st.write(max_sharpe_opt_allocation)
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to draw graph </h3>", unsafe_allow_html=True)

st.markdown("## Minimum Volatility portfolio")
st.latex(r'''\begin{aligned}
        & \underset{w}{\text{minimize}}
        & & W^T \Sigma W \\
        & \text{subject to}
        & &  W^T 1 = 1 \\
        & && W \geq 0 \\
        \end{aligned}''')

try:
        # calculate weight of min vol portfolio
        w_opt_vol = calculate_min_vol_opt_allocation(n_stocks,  cov_matrix)
        min_vol_opt_allocation = pd.DataFrame(w_opt_vol['x'], index=returns_df.columns, columns=['allocation'])
        min_vol_opt_allocation.allocation = [round(i*100,2)for i in min_vol_opt_allocation.allocation]
        min_vol_opt_Return, min_vol_opt_Volatility, min_vol_opt_sharpe_Ratio = calculate(w_opt_vol['x'], mean_returns, cov_matrix, risk_free_rate)
        min_vol_opt_allocation = min_vol_opt_allocation.T
        # display
        st.write("Minimum Volatility Optimal Portfolio Allocation (Percentage)")
        st.write(min_vol_opt_allocation)
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to draw graph </h3>", unsafe_allow_html=True)

st.markdown("## The Minimum Risk Mean-Variance Portfolio (Efficient Markowitz Frontier)")
st.markdown("We can also plot a line on the graph that represents the efficient portfolios for a specific risk level, known as the 'efficient frontier'. \
                This frontier is determined by taking into account two constraints: the first constraint being that the sum of weights allocated to the portfolio must equal 1, \
                and the second constraint being the calculation of the most efficient portfolio for a given target return.")
st.latex(r'''\begin{aligned}
        & \underset{w}{\text{minimize}}
        & & W^T \Sigma W \\
        & \text{subject to}
        & &  W^T \hat{\mu} = \bar{r} \\
        & &&  W^T 1 = 1 \\
        & && W \geq 0 \\
        \end{aligned}''')
try:
        volatility_opt, simulate_returns = calculate_opt_allocation(n_stocks, mean_returns, cov_matrix, expected_Return, max_sharpe_index, min_volality_index)

        st.pyplot(portfolio_optimization_graph(returns_df, mean_returns, expected_Volatility, expected_Return, sharpe_Ratio, \
                                        max_sharpe_opt_Volatility, max_sharpe_opt_Return, min_vol_opt_Volatility, min_vol_opt_Return, volatility_opt, simulate_returns))
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to draw graph </h3>", unsafe_allow_html=True)


st.markdown("# Optimal Portfolio")
st.markdown("## Capital Allocation Line")
st.markdown("The Capital Allocation Line (CAL) here assumes an investor allocates a weighted portfolio of cash and/or the optimised sharpe ratio portfolio. The line is plotted on the same axis of the Efficient Frontier.")
st.markdown("The line (blue line in plot below) intersects the y-axis where the investor holds 100% risk free asset, where the rate of return is the dividend of a bond. The line intersects Efficient Frontier when the \
                investor holds 100% of the Sharpe Optimised portfolio. If the portfolio hold is risk taking it can take loans where Sharpe Optimised portfolio is more that 100% and cash is less than 0%.")
st.markdown("There is a linear relationship in returns, because the entire portfolio only has 2 components and as the risky portfolio weight decreases the returns decrease monotonously.")
st.latex(r''' E(R_p) = r_f + \frac{E(R) - r_f}{\sigma_i} \sigma_p ''')


st.markdown("## Utility Function")
st.latex(r'''U = E(R) - 0.5 A \sigma ^2''')
st.markdown("This function is from an economic model. Utility is as expressed as returns and is discounted by the level of realised risk. \
                The coefficient of risk aversion is A. If an invest is less risk, risk averse A is small. \
                Expected return, E(R) is proportionate to the level of utility")

a = st.number_input('Insert risk averse (Default is 30)', value = 30)
try:
        st.pyplot(capital_allocation_line_graph(a, risk_free_rate, expected_Return, expected_Volatility, sharpe_Ratio, 
                                max_sharpe_opt_Return, max_sharpe_opt_Volatility, max_sharpe_opt_sharpe_Ratio,
                                min_vol_opt_Volatility, min_vol_opt_Return, 
                                volatility_opt, simulate_returns))
        
        # calculate annualised volatility
        an_vol = np.std(returns_df) * np.sqrt(250)
        # calculate annualised return
        an_rt = mean_returns * 250


        st.write("Optimal maximum Sharpe Ratio Portfolio Allocation (Percentage):")
        st.write("Annualised Return: {}".format(round(max_sharpe_opt_Return, 2)))
        st.write("Annualised Volatility: {}".format(round(max_sharpe_opt_Volatility, 2)))
        st.write(max_sharpe_opt_allocation)

        st.write("Optimal minimum Volatility Portfolio Allocation (Percentage):")
        st.write("Annualised Return: {}".format(round(min_vol_opt_Return, 2)))
        st.write("Annualised Volatility: {}".format(round(min_vol_opt_Volatility, 2)))
        st.write(min_vol_opt_allocation )

        st.write("Individual Stock Returns and Volatility")
        for i, txt in enumerate(returns_df.columns):
                st.write( "{}: annuaised return: {}, annualised volatility:{}".format(txt, round(an_rt[i], 2), round(an_vol[i], 2)))
except:
        st.markdown("<h3 style='text-align: center; color: green;'>Choose stock options to draw graph </h3>", unsafe_allow_html=True)
