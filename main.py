from settings import settings
from object_factory import object_factory
from mappers import portfolios_allocation_mapper

def generate_optimum_portfolio():
    
    obj_factory = object_factory(settings)
    ce = obj_factory.get_companies_extractor()
    cp = obj_factory.get_charts_plotter()
    mcs = obj_factory.get_portfolio_generator()
    fr = obj_factory.get_file_repository()
    mc = obj_factory.get_metrics_calculator()
    

    print('1. Get companies')
    companies = ce.get_companies_list()
    price_extractor = obj_factory.get_price_extractor(companies)
    print('2. Get company stock prices')
    
    end_date = settings.get_end_date()
    start_date = settings.get_start_date(end_date)
    closing_prices = price_extractor.get_prices(settings.PriceEvent, start_date, end_date)

    
    # vytvori graf ceny akcii a da do tabulky
    cp.plot_prices(closing_prices)    
    fr.save_to_file(closing_prices, 'StockPrices')

    print('3. Calculate Daily Returns')    
    returns = settings.DailyAssetsReturnsFunction(closing_prices, settings.ReturnType)
    #graf dennich navratu a da do tabulky
    cp.plot_returns(returns)
    fr.save_to_file(returns, 'Returns')

    print('4. Calculate Expected Mean Return & Covariance')
    expected_returns = settings.AssetsExpectedReturnsFunction(returns)
    covariance = settings.AssetsCovarianceFunction(returns)
    #graf + da do tabulky
    cp.plot_correlation_matrix(returns)
    fr.save_to_file(covariance, 'Covariances')

    print('5. Use Monte Carlo Simulation')
    
    #generuje portfolia s alokaci
    portfolios_allocations_df = mcs.generate_portfolios(expected_returns, covariance, settings.RiskFreeRate)
    portfolio_risk_return_ratio_df = portfolios_allocation_mapper.map_to_risk_return_ratios(portfolios_allocations_df)
    
    
    #graf portfolii, vytiskne sharpuv pomer a da do tabulky
    cp.plot_portfolios(portfolio_risk_return_ratio_df)
    max_sharpe_portfolio = mc.get_max_sharpe_ratio(portfolio_risk_return_ratio_df)['Portfolio']
    max_shape_ratio_allocations = portfolios_allocations_df[[ 'Symbol', max_sharpe_portfolio]]
    print(max_shape_ratio_allocations)
    fr.save_to_file(portfolios_allocations_df, 'MonteCarloPortfolios')
    fr.save_to_file(portfolio_risk_return_ratio_df, 'MonteCarloPortfolioRatios')   
    
    print('6. Use an optimiser')
    #generuje optimalni portfolia
    targets = settings.get_my_targets()    
    optimiser = obj_factory.get_optimiser(targets, len(expected_returns.index))    
    portfolios_allocations_df = optimiser.generate_portfolios(expected_returns, covariance, settings.RiskFreeRate)
    portfolio_risk_return_ratio_df = portfolios_allocation_mapper.map_to_risk_return_ratios(portfolios_allocations_df)

    #da do grafu efektivni hranici
    cp.plot_efficient_frontier(portfolio_risk_return_ratio_df)
    cp.show_plots()

    #ulozi tabulku
    print('7. Saving Data')
    fr.save_to_file(portfolios_allocations_df, 'OptimisationPortfolios')
    fr.close()

generate_optimum_portfolio()
