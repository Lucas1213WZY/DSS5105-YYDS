# generate report


df['YearDate'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')  # Example for generating YearDate column

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html, Input, Output
from flask import send_file

# Sample emission data for business travel and procurement
emission_data = {
    'Business Travel Hotel Emission': 1780.0,
    'Business Travel Flight Emission': 13879.999999999998,
    'Business Procurement Airline Emission': 5965.0,
    'Business Procurement Diesel Truck Emission': 159.0,
    'Business Procurement Electric Truck Emission': 24.0
}

# Example of new data (from your example)
building_data = {
    'Building Name': 'EQUINIX SG3 DATA CENTRE',
    'Postcode': '139963',
    'Year': 2023,
    'latitude': 1.2767,
    'longitude': 103.8452,
    'Address': '26A AYER RAJAH CRESCENT, SINGAPORE',
    'Type': 'Commercial Building',
    'GM Version': 'Existing Data Centres',
    'Validation Result': 'Pass',
    'YearDate': '2023-01-01',
    'total_ghg': 3812.165039,
    'ghg_intensity_predicted': 0.108245,
    'predicted_greenmarks': 'platinum',
    'threshold': 0.1
}

# Calculate the total emission from business travel and procurement transportation
total_emission = (emission_data['Business Travel Hotel Emission'] + 
                  emission_data['Business Travel Flight Emission'] + 
                  emission_data['Business Procurement Airline Emission'] + 
                  emission_data['Business Procurement Diesel Truck Emission'] + 
                  emission_data['Business Procurement Electric Truck Emission'])

# Callback for generating the HTML report on Page 4
@app.callback(
    Output('download-report', 'data'),
    Input('report-button', 'n_clicks')
)
def generate_report(n_clicks):
    if n_clicks:
        try:
            # Static title for the report
            report_title = "ESG Performance Analysis Report"

            # Title section for HTML/PDF
            title_section = f"<h1 style='text-align:center;'>{report_title}</h1>"

            # Content for each report section
            executive_summary = """
            <h2>Executive Summary</h2>
            <p>This report provides a comprehensive analysis of greenhouse gas (GHG) emissions data, resource usage, and benchmarking based on the dataset uploaded to our platform. Key findings highlight patterns in emissions intensity over time, the breakdown of emissions by scope, and comparative benchmarking based on recognized certification levels.</p>
            """

            introduction = """
            <h2>Introduction to ESG Reporting Analysis</h2>
            <p><strong>Purpose of the Analysis</strong></p>
            <p>ESG reporting is increasingly critical for understanding the environmental impact and sustainability performance of organizations. This report leverages our platform’s analytics to provide a data-driven view of the submitted dataset, focusing on GHG emissions and resource management metrics.</p>
            
            <h2>Methodology</h2>
            <p><strong>Data Processing and Visualization</strong></p>
            <p>The uploaded dataset underwent several stages of processing, including data quality checks, normalization, and segmentation by relevant categories (e.g., certification levels, emissions scopes). For commuting data in Scope 3, we have regional factors to adjust your value.</p>
            
            <p><strong>Automated Analysis and Model Selection</strong></p>
            <p>This analysis was conducted through our platform’s advanced analytics, which includes an automated model selection process to identify the best statistical or machine learning model for your data type. By evaluating multiple models based on their fit and predictive accuracy, the platform ensures that each analysis component—such as trend detection, emissions distribution, and resource usage breakdown—is optimized for accuracy and relevance.</p>
            """

            scope_of_reporting = """
            <h2>Scope of Reporting</h2>
            <p><strong>Reporting Period</strong></p>
            <p>The analysis covers data entries from January 1, 2023, to December 31, 2023. All findings are based on the data within this timeframe, as provided in the uploaded dataset.</p>
            
            <p><strong>Data Boundaries</strong></p>
            <p>The dataset includes various entities, each contributing to the total emissions and resource metrics. This report reflects the aggregated and segmented data as processed by our platform, without further boundary restrictions or exclusions.</p>
            """

            # Emission data section for report, including new data
            emission_section = f"""
            <h2>Emission Breakdown</h2>
            <p>The following details summarize key emission and sustainability data for the selected building:</p>

            <p><strong>Total GHG Emissions:</strong> {building_data['total_ghg']} CO2e</p>
            <p><strong>Predicted GHG Intensity:</strong> {building_data['ghg_intensity_predicted']} kg CO2e/m²</p>
            <p><strong>Predicted Green Marks Certification:</strong> {building_data['predicted_greenmarks']}</p>

            <p>The following table summarizes the emissions associated with different business activities:</p>
            <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; text-align: left;">
                <tr>
                    <th>Emission Source</th>
                    <th>Emission (in CO2e)</th>
                </tr>
                <tr><td>Business Travel Hotel Emission</td><td>{emission_data['Business Travel Hotel Emission']}</td></tr>
                <tr><td>Business Travel Flight Emission</td><td>{emission_data['Business Travel Flight Emission']}</td></tr>
                <tr><td>Business Procurement Airline Emission</td><td>{emission_data['Business Procurement Airline Emission']}</td></tr>
                <tr><td>Business Procurement Diesel Truck Emission</td><td>{emission_data['Business Procurement Diesel Truck Emission']}</td></tr>
                <tr><td>Business Procurement Electric Truck Emission</td><td>{emission_data['Business Procurement Electric Truck Emission']}</td></tr>
                <tr><td><strong>Total Emission from Business Travel and Procurement</strong></td><td><strong>{total_emission}</strong></td></tr>
            </table>
            """

            performance_data_intro = """
            <h2>Performance Data</h2>
            <p>This section provides detailed insights derived from the GHG emissions and resource usage data.</p>
            """

            benchmark_intro = """
            <h2>Benchmark</h2>
            <p>The benchmarking section compares the entities based on certification or award levels to highlight how the dataset aligns with established standards.</p>
            """

            future_outlook = """
            <h2>Future Insights and Recommendations</h2>
            <p>Based on the analysis conducted through our platform, the following insights and recommendations can guide future actions:</p>
            <ul>
                <li><strong>Focus on High Emission Scopes</strong>: Entities or operations with high Scope 1, Scope 2, or Scope 3 emissions should be prioritized for reduction strategies, as identified in the scope distribution analysis.</li>
                <li><strong>Enhance Resource Efficiency</strong>: The water and waste distribution insights suggest potential areas for improving resource efficiency. Reducing waste generation and optimizing water usage can directly contribute to better sustainability outcomes.</li>
                <li><strong>Targeted Certification Improvement</strong>: For entities with lower certification levels, consider strategies to meet higher certification standards. This can enhance overall ESG performance and align with sustainability benchmarks.</li>
                <li><strong>Emissions Intensity Management</strong>: The observed GHG intensity trend over time highlights areas where emissions management may be improved. Continuous monitoring and mitigation efforts during high-intensity periods could further reduce the overall environmental footprint.</li>
            </ul>
            """

            # Generate and aggregate plots
            # Awards Distribution plot
            benchmark_data = df.groupby('Award').agg(unique_building_count=('Building Name', 'nunique')).reset_index()
            fig_awards = go.Figure(data=[go.Scatter(
                x=[0, 1, 2, 3], y=[2, 2, 2, 2], mode='markers+text',
                marker=dict(size=benchmark_data["unique_building_count"], opacity=0.6, color="#365E32"),
                text=benchmark_data["Award"],
                textposition="top center",
                hovertext=benchmark_data["unique_building_count"]
            )])
            fig_awards.update_layout(title="Awards Distribution", showlegend=False,
                                     xaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False),
                                     yaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False))
            awards_plot_html = fig_awards.to_html(full_html=False, include_plotlyjs='cdn')

            # Performance Data plot (Aggregated GHG Intensity over time)
            year_trend_df = df.groupby('YearDate').agg({'GHG_Intensity': 'mean'}).reset_index()
            fig_performance = px.line(
                year_trend_df,
                x='YearDate',
                y='GHG_Intensity',
                title="Average Greenhouse Gas Emissions Intensity Over Time",
                labels={"GHG_Intensity": "Average GHG Intensity"}
            )
            fig_performance.update_traces(line=dict(color="#365E32"))
            performance_plot_html = fig_performance.to_html(full_html=False, include_plotlyjs='cdn')

            # GHG Intensity Violin Plot (under Benchmark)
            fig_violin = px.violin(df, x="GHG_Intensity", box=True, points='all', title="GHG Intensity Violin Plot",
                                   labels={"GHG_Intensity": "Greenhouse Gas Emissions Intensity"})
            fig_violin.update_traces(marker=dict(color="green"))
            violin_plot_html = fig_violin.to_html(full_html=False, include_plotlyjs='cdn')

            # Water and Waste Distribution Plot (under Performance Data)
            pie_data_ww = pd.melt(df[['Building Name', 'Water', 'Waste']], id_vars='Building Name', var_name='key', value_name='value')
            pie_data_ww = pie_data_ww.groupby('key').agg({"value": 'sum'}).reset_index()
            fig_water_waste = px.pie(pie_data_ww, names='key', values='value', title="Water and Waste Distribution")
            fig_water_waste.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
            water_waste_plot_html = fig_water_waste.to_html(full_html=False, include_plotlyjs='cdn')

            # Scope Emissions Distribution Plot (under Performance Data)
            pie_data_scope = pd.melt(df[['Building Name', 'Scope1', 'Scope2', 'Scope3']], id_vars='Building Name', var_name='key', value_name='value')
            pie_data_scope = pie_data_scope.groupby('key').agg({"value": 'sum'}).reset_index()
            fig_scope_emissions = px.pie(pie_data_scope, names='key', values='value', title="Scope Emissions Distribution")
            fig_scope_emissions.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
            scope_emissions_plot_html = fig_scope_emissions.to_html(full_html=False, include_plotlyjs='cdn')

            # Generate report based on the selected format
            report_html = f"""
            <html>
                    <body>
                    <!-- Logo at the top of the report -->
                    <div style="text-align: center; margin-bottom: 20px;">
                    <img src="./assets/teamlogo.png" alt="Company Logo" style="width: 200px; height: auto;">
                    </div>
                        {title_section}
                        {executive_summary}
                        {introduction}
                        {scope_of_reporting}
                        {emission_section}  <!-- Emission data section comes before Performance data -->
                        {performance_data_intro}
                        {performance_plot_html}
                        {water_waste_plot_html}
                        {scope_emissions_plot_html}
                        {benchmark_intro}
                        {awards_plot_html}
                        {violin_plot_html}
                        {future_outlook}
                    </body>
                </html>
                """
            # Save the HTML report
            with open('report.html', 'w') as f:
                f.write(report_html)
            return dcc.send_file('report.html')
        except Exception as e:
            print(f"Error during report generation: {e}")
            return None
