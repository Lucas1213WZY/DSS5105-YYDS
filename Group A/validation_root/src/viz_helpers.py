import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class ValidationVisualizer:
    """Visualization helpers for Green Mark validation results"""
    def __init__(self):
        # Set style
        sns.set_style("whitegrid")
        self.colors = {
            'primary': '#4A7BF7',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'scope1': '#4A7BF7',  # Blue for Scope 1
            'scope2': '#4CAF50',  # Green for Scope 2
            'scope3': '#FFC107'   # Yellow for Scope 3
        }

    def plot_ghg_results(self, result):
        """
        Create GHG results display panel
        Args:
            result (dict): Validator result dictionary
        """
        fig = plt.figure(figsize=(10, 6))
        
        # Total GHG Emissions
        plt.subplot(3, 1, 1)
        plt.text(0.5, 0.5, f"{result['ghg_results']['total_ghg']:.2f} tCO2e",
                fontsize=24, color=self.colors['primary'], horizontalalignment='center')
        plt.text(0.5, 0.8, "Total GHG Emissions", fontsize=14, horizontalalignment='center')
        plt.axis('off')
        
        # GHG Intensity
        plt.subplot(3, 1, 2)
        plt.text(0.5, 0.5, f"{result['ghg_results']['ghg_intensity']:.4f} tCO2e/m²",
                fontsize=24, color=self.colors['success'], horizontalalignment='center')
        plt.text(0.5, 0.8, "GHG Intensity", fontsize=14, horizontalalignment='center')
        plt.axis('off')
        
        # Predicted Level
        plt.subplot(3, 1, 3)
        plt.text(0.5, 0.5, result['green_mark']['predicted_level'].upper(),
                fontsize=24, color='#CD853F',  # Golden brown for Green Mark level
                horizontalalignment='center')
        plt.text(0.5, 0.8, "Predicted Level", fontsize=14, horizontalalignment='center')
        plt.axis('off')
        
        plt.tight_layout()
        return fig

    def plot_emissions_breakdown(self, result):
        """
        Create emissions breakdown pie chart
        Args:
            result (dict): Validator result dictionary
        """
        # Calculate percentages
        scope1 = result['ghg_results']['breakdown']['scope1']
        scope2 = result['ghg_results']['breakdown']['scope2']
        scope3 = result['ghg_results']['breakdown']['scope3']
        total = scope1 + scope2 + scope3
        
        values = [
            (scope1/total)*100,
            (scope2/total)*100,
            (scope3/total)*100
        ]
        
        labels = [
            f'Scope 1: {values[0]:.0f}%',
            f'Scope 2: {values[1]:.0f}%',
            f'Scope 3: {values[2]:.0f}%'
        ]
        
        colors = [self.colors['scope1'], self.colors['scope2'], self.colors['scope3']]
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        plt.title("Emissions Breakdown", pad=20)
        return fig

    def plot_benchmarks(self, result):
        """
        Create benchmark comparison bar chart
        Args:
            result (dict): Validator result dictionary
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        # Get benchmarks and current intensity
        benchmarks = {
            'Platinum': 0.1,
            'GoldPLUS': 0.12,
            'Gold': 0.15,
            'Certified': 0.2
        }
        current = result['ghg_results']['ghg_intensity']
        
        # Create bar chart
        x = np.arange(len(benchmarks) + 1)
        bars = ax1.bar(['Current'] + list(benchmarks.keys()), 
                      [current] + list(benchmarks.values()))
        
        # Color coding
        bars[0].set_color(self.colors['success'])
        for bar in bars[1:]:
            bar.set_color(self.colors['primary'])
            
        # Customize chart
        ax1.set_ylabel('GHG Intensity (tCO2e/m²)')  
        ax1.set_title('Green Mark Benchmarks')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Add performance analysis
        current_level = result['green_mark']['predicted_level']
        next_level = self._get_next_level(current_level)
        if next_level:
            next_threshold = benchmarks[next_level]
            improvement = ((current - next_threshold) / current) * 100
            analysis_text = (f"Below threshold by {abs(improvement):.2f}%\n"
                           f"Next Level: {next_level}")
            ax2.text(0.5, 0.5, analysis_text,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color=self.colors['success'])
        ax2.axis('off')
        
        plt.tight_layout()
        return fig

    def _get_next_level(self, current_level):
        """Helper to determine next Green Mark level"""
        levels = ['Certified', 'Gold', 'GoldPLUS', 'Platinum']
        try:
            current_idx = levels.index(current_level.capitalize())
            if current_idx < len(levels) - 1:
                return levels[current_idx + 1]
        except ValueError:
            pass
        return None
    
# Example usage
if __name__ == "__main__":
    # Example validator result
    result = {
        'success': True,
        'ghg_results': {
            'total_ghg': 3924.94,
            'ghg_intensity': 0.1114,
            'breakdown': {
                'scope1': 82.74,
                'scope2': 1852.64,
                'scope3': 1989.55,
            }
        },
        'green_mark': {
            'predicted_level': 'goldplus',
            'threshold': 0.132
        }
    }
    
    # Create visualizations
    viz = ValidationVisualizer()
    
    # Plot GHG results
    ghg_fig = viz.plot_ghg_results(result)
    ghg_fig.savefig('ghg_results.png', bbox_inches='tight', dpi=300)
    
    # Plot emissions breakdown
    breakdown_fig = viz.plot_emissions_breakdown(result)
    breakdown_fig.savefig('emissions_breakdown.png', bbox_inches='tight', dpi=300)
    
    # Plot benchmarks
    benchmarks_fig = viz.plot_benchmarks(result)
    benchmarks_fig.savefig('benchmarks.png', bbox_inches='tight', dpi=300)