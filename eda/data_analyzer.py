import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

from itertools import combinations

from logs.log_manager import LogManager
from utils.parquet_handler import ParquetHandler

class DataAnalyzer:
    def __init__(self, log_manager: LogManager, parquet_handler: ParquetHandler, output_path: str = "eda/plots"):
        self.log_manager = log_manager
        self.parquet_handler = parquet_handler
        self.output_path = output_path
        self.data = None

    def perform_full_analysis(self, parquet_file_path: str, figsize: tuple[int, int] = (10, 8), annot: bool = True, cmap: str = 'coolwarm', fmt: str = ".2f", prefix: str = "data", sample_size: int = 1000):

        self.data = self.parquet_handler.scan_parquet(parquet_file_path)

        self._check_and_create_output_directory()

        # 1. Summary Statistics
        self.generate_summary_statistics()

        # 2. Missing Values and Duplicated Analysis
        self.analyze_missing_values()
        self.analyze_duplicates()

        # 3. Correlation Analysis
        self.analyze_correlation(figsize=figsize, annot=annot, cmap=cmap, fmt=fmt, prefix=prefix, sample_size=sample_size)

        # 4. Data Distribution (Violin, Scatter, Distribution plots)
        self.analyze_data_distribution(figsize=figsize, prefix=prefix, sample_size=sample_size)

        # 5. Skewness and Kurtosis
        self.analyze_skewness()
        self.analyze_kurtosis()

    def _check_and_create_output_directory(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            self.log_manager.log("INFO", f"Output directory created at {self.output_path}")
        else:
            self.log_manager.log("INFO", f"Output directory already exists at {self.output_path}")

    def _check_data_loaded(self):
        if self.data is None:
            self.log_manager.log("ERROR", "Data not loaded. Please load data before performing analysis.")
            raise ValueError("Data not loaded. Please load data before performing analysis.")

    def _get_numeric_columns(self):
        self._check_data_loaded()
        numeric_columns = [col for col, dtype in self.data.schema.items() if dtype in (pl.Int64, pl.Int32, pl.Float64, pl.Float32)]

        # remove goodreads_id from the list if it exists
        if 'goodreads_id' in numeric_columns:
            numeric_columns.remove('goodreads_id')

        if 'book_id' in numeric_columns:
            numeric_columns.remove('book_id')

        return numeric_columns

    def generate_summary_statistics(self):
        self._check_data_loaded()
        try:
            print("Summary Statistics:")
            print(self.data.describe())
            print("\n")
        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to generate summary statistics: {e}")
            raise

    def analyze_missing_values(self):
        self._check_data_loaded()
        try:
            print("Missing Values Analysis:")
            print(self.data.null_count())
            print("\n")
        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to analyze missing values: {e}")
            raise

    def analyze_duplicates(self):
        self._check_data_loaded()
        try:
            print("Duplicated Rows Analysis:")
            print(self.data.is_duplicated().sum())
            print("\n")
        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to analyze duplicated rows: {e}")
            raise

    def analyze_correlation(self, figsize: tuple[int, int] = (10, 8), annot: bool = True, cmap: str = 'coolwarm', fmt: str = ".2f", prefix: str = "correlation", sample_size: int = 1000):
        self._check_data_loaded()
        try:
            numeric_columns = self._get_numeric_columns()
            if not numeric_columns:
                self.log_manager.log("WARNING", "No numeric columns found for correlation analysis.")
                return

            sampled_data = self.data.sample(n=min(sample_size, self.data.height), seed=42)

            correlation_matrix = sampled_data.select(numeric_columns).corr()
            print("Correlation Analysis:")
            print(correlation_matrix)
            print("\n")

            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

            plt.figure(figsize=figsize)

            # labels
            ax = sns.heatmap(correlation_matrix,
                            center=0,
                            annot=annot,
                            cmap=cmap,
                            fmt=fmt,
                            mask=mask,
                            xticklabels=correlation_matrix.columns,
                            yticklabels=correlation_matrix.columns,
                            annot_kws={"size": 10},
                            linewidths=0.5)

            plt.title(f'Correlation Matrix of Numerical Variables')


            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

            plt.tight_layout()

            plt.savefig(f'{self.output_path}/{prefix}_correlation_matrix.png')
            self.log_manager.log("INFO", f"Correlation matrix saved to {self.output_path}/{prefix}_correlation_matrix.png")
        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to analyze correlation: {e}")
            raise

    def analyze_data_distribution(self, figsize: tuple[int, int] = (12, 8), prefix: str = "data_distribution", sample_size: int = 1000):
        self._check_data_loaded()

        self._plot_all_violin_plots(figsize=figsize, prefix=prefix, sample_size=sample_size)

        self._plot_all_distribution_plots(figsize=figsize, prefix=prefix, sample_size=sample_size)

        self._plot_all_scatter_plots(figsize=figsize, prefix=prefix, sample_size=sample_size)

    def _plot_all_violin_plots(self, figsize: tuple[int, int] = (12, 8), prefix: str = "violin", sample_size: int = 1000):
        try:

            sampled_data = self.data.sample(n=min(sample_size, self.data.height), seed=42)

            numeric_columns = self._get_numeric_columns()
            if not numeric_columns:
                self.log_manager.log("WARNING", "No numeric columns found for violin plot analysis.")
                return

            _, axes = plt.subplots(figsize=figsize)

            # rotate x-axis labels for better readability
            axes.set_xticks(range(len(numeric_columns)))
            axes.set_xticklabels(numeric_columns, rotation=45, ha="right")

            sns.violinplot(data=sampled_data[numeric_columns], ax=axes, inner="quartile")
            axes.set_title("Violin Plots of Numerical Variables")
            axes.set_ylabel("Value")
            axes.set_xlabel("Feature")
            plt.subplots_adjust(hspace=0.5, wspace=0.3)
            plt.tight_layout()

            plt.savefig(f'{self.output_path}/{prefix}_all_violin.png')

            self.log_manager.log("INFO", f"Violin plots saved to {self.output_path}/{prefix}_all_violin.png")

        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to plot violin plots: {e}")
            raise

    def _plot_all_distribution_plots(self, figsize: tuple[int, int] = (12, 8), prefix: str = "distribution", sample_size: int = 1000):

        try:
            sampled_data = self.data.sample(n=min(sample_size, self.data.height), seed=42)

            numeric_columns = self._get_numeric_columns()
            num_cols = len(numeric_columns)
            num_rows = (num_cols // 3) + (1 if num_cols % 3 != 0 else 0)  # 3 gráficos por linha

            fig, axes = plt.subplots(num_rows, 3, figsize=figsize)
            axes = axes.flatten()

            for i, feature in enumerate(numeric_columns):
                ax = axes[i]
                sns.histplot(sampled_data[feature], ax=ax, kde=True)
                ax.set_ylabel("Frequency")
                ax.set_title(f"Distribution of {feature}")
                ax.set_xlabel(feature)

            # Remove the empty subplots
            for j in range(len(numeric_columns), len(axes)):
                fig.delaxes(axes[j])

            # Adjust the layout
            plt.subplots_adjust(hspace=0.5, wspace=0.3)
            plt.tight_layout()

            # Save the plot
            plt.savefig(f'{self.output_path}/{prefix}_all_distributions.png')
            self.log_manager.log("INFO", f"Distribution plots saved to {self.output_path}/{prefix}_all_distributions.png")

        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to plot distribution plots: {e}")
            raise

    def _plot_all_scatter_plots(self, figsize: tuple[int, int] = (12, 8), prefix: str = "scatter", sample_size: int = 1000, dpi: int = 100):
        try:
            numeric_columns = self._get_numeric_columns()
            comb = list(combinations(numeric_columns, 2))

            # Create all possible combinations of 2 features
            for _, (x_feature, y_feature) in enumerate(comb):

                # Create a descriptive title for the plot
                title = f"{prefix} {x_feature} vs {y_feature}"

                save_path = f'{self.output_path}/{title}.png'

                sampled_data = self.data.sample(n=min(sample_size, self.data.height), seed=42)

                self._create_and_save_scatter_plot(sampled_data, x_feature, y_feature, save_path, title, figsize, dpi)

        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to plot scatter plots: {e}")
            raise

    def _create_and_save_scatter_plot(self, 
                                    df: pl.DataFrame, 
                                    x_feature: str, 
                                    y_feature: str, 
                                    save_path: str, 
                                    title: str = None, 
                                    figsize: tuple = (10, 6), 
                                    dpi: int = 100) -> None:

        try:

            plt.figure(figsize=figsize, dpi=dpi)

            sns.regplot(data=df, x=x_feature, y=y_feature, )

            if title:
                plt.title(title)

            plt.xlabel(x_feature)
            plt.ylabel(y_feature)

            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()

        except KeyError:
            print(f"Error: Feature '{x_feature}' or '{y_feature}' not found in DataFrame.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def analyze_skewness(self):
        self._check_data_loaded()

        try:
            numeric_columns = self._get_numeric_columns()
            if not numeric_columns:
                self.log_manager.log("WARNING", "No numeric columns found for skewness analysis.")
                return

            skewness_info = {}
            for col in numeric_columns:
                skewness_value = self.data[col].skew()
                skewness_info[col] = skewness_value

            print("Skewness Analysis:")
            for col, skewness in skewness_info.items():
                print(f"Column: {col}, Skewness: {skewness}")
            print("\n")

        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to analyze skewness: {e}")
            raise

    def analyze_kurtosis(self):
        self._check_data_loaded()

        try:
            numeric_columns = self._get_numeric_columns()
            if not numeric_columns:
                self.log_manager.log("WARNING", "No numeric columns found for kurtosis analysis.")
                return

            kurtosis_info = {}
            for col in numeric_columns:
                kurtosis_value = self.data[col].kurtosis()
                kurtosis_info[col] = kurtosis_value

            print("Kurtosis Analysis:")
            for col, kurtosis in kurtosis_info.items():
                print(f"Column: {col}, Kurtosis: {kurtosis}")
            print("\n")

        except Exception as e:
            self.log_manager.log("ERROR", f"Failed to analyze kurtosis: {e}")
            raise