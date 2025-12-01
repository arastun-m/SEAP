""" Tables and Plotting/Charting for Evaluation Results 

1. CLUVis: Conversational Language Understanding Visualisation
2. CQAVis: Conversational Question Answering Visualisation
3. RAGVis: Retrieval-Augmented Generation Visualisation
4. AgentVis: Modular Agent Performance Visualisation
5. EndToEndVis: End-to-End System Performance Visualisation

- Color Scheme: viridis set2
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
from typing import List

from eval_config import RESULT_PATHS, FIG_PATHS
from eval_utils import EvalDataHandling


def calc_response_level_metrics(data) -> None:
    """ Calculates average response level metrics; answer length and latency from evaluation results. """
    if not data or data.get("rows") is None or len(data["rows"]) == 0:
        print("No evaluation results found. Please run evaluation first.")
        return 
    
    total_answer_length = 0
    total_latency = 0
    for item in data["rows"]:
        total_answer_length += item.get("inputs.answer_length", 0)
        total_latency += item.get("inputs.latency", 0)
    num_responses = len(data["rows"])
    return (total_answer_length / num_responses, total_latency / num_responses)


class CLUVis:
    def __init__(self) -> tuple[pd.DataFrame, dict]:
        """
        Preprocess results from a JSON file into a DataFrame and metrics dictionary.
        """
        self.clu_figure_filename_st = FIG_PATHS["clu"]  # start of filename for CLU figures
        eval_data_handler = EvalDataHandling()
        data = eval_data_handler.get_eval_results(RESULT_PATHS["clu"])
        data_old = eval_data_handler.get_eval_results(RESULT_PATHS["clu_old"])  # for old CLU results

        # convert metrics into a dict
        metrics = data.get('metrics', {})
        metrics["average_answer_length"], metrics['average_latency'] = calc_response_level_metrics(data)
        #metrics['average_answer_length'], metrics['average_latency'] = calc_response_level_metrics(data)
        # convert results into a dataframe
        results_df = pd.DataFrame(data['rows'])
        # rename flattened keys to clean column names
        results_df = results_df.rename(columns={
            'inputs.query': 'query',
            'inputs.context': 'context',
            'inputs.response': 'response',
            'inputs.ground_truth': 'ground_truth',
            'inputs.latency': 'latency',\
            'inputs.answer_length': 'answer_length',
            'outputs.f1_score.f1_score': 'f1_score',
            'outputs.f1_score.f1_result': 'f1_result',
            'outputs.f1_score.f1_threshold': 'f1_threshold'
        })

        results_old_df = pd.DataFrame(data_old['rows'])
        # rename flattened keys to clean column names
        results_old_df = results_old_df.rename(columns={
            'inputs.query': 'query',
            'inputs.context': 'context',
            'inputs.response': 'response',
            'inputs.ground_truth': 'ground_truth',
            'outputs.f1_score.f1_score': 'f1_score',
            'outputs.f1_score.f1_result': 'f1_result',
            'outputs.f1_score.f1_threshold': 'f1_threshold'
        })
        
        self.results_df = results_df
        self.results_df_old = results_old_df
        self.metrics = metrics

    def clu_intend_coverage(self) -> None:
        # percentage of each intend covered (intend.counts / total_intends)
        intend_counts = self.results_df['ground_truth'].value_counts(normalize=True) * 100
        # pie chart (percentage of each intend covered)
        plt.figure(figsize=(10, 8))
        plt.pie(intend_counts, labels=intend_counts.index, autopct='%1.1f%%', startangle=140)
        plt.title('Intend Coverage by CLU Model')
        plt.legend(title='Intends', loc='upper right')
        plt.text(0, -1.2, f'Number of samples: {len(self.results_df['query'])}', ha='center', fontsize=12, color='black')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()
        plt.savefig(f"{self.clu_figure_filename_st}_intend_coverage.png")
    
    def clu_total_passrate_comparison_table(self) -> None:
        """Comparison of total pass rate and latency between old and new CLU results."""
        old_pass_rate = (self.results_df_old['f1_result'] == 'pass').mean() * 100
        new_pass_rate = (self.results_df['f1_result'] == 'pass').mean() * 100
        old_cqa_pass_rate = (self.results_df_old[self.results_df_old['ground_truth'] == 'CQA']['f1_result'] == 'pass').mean() * 100
        comparison_df = pd.DataFrame({
            'Model Version': ['Old CLU', 'New CLU'],
            'Total Pass Rate (%)': [old_pass_rate, new_pass_rate],
        })
        print("Total Pass Rate Comparison:"
              f"\n{comparison_df.to_string(index=False)}")
        print("old CLU CQA pass rate", old_cqa_pass_rate)

    def clu_performance_breakdown_table(self) -> None:
        """
        Table of pass/fail for all intends pass/total counts and average latency per intend.
        """
        # get pass/fail counts
        pass_fail_counts = self.results_df.groupby('ground_truth')['f1_result'].value_counts().unstack(fill_value=0)
        # calculate pass/total counts
        pass_fail_counts['total'] = pass_fail_counts.sum(axis=1)
        pass_fail_counts['pass'] = pass_fail_counts.get('pass', 0)
        pass_fail_counts['fail'] = pass_fail_counts.get('fail', 0)
        pass_fail_counts['pass_rate'] = (pass_fail_counts['pass'] / pass_fail_counts['total']) * 100
        # calculate average latency per intend
        avg_latency = self.results_df.groupby('ground_truth')['latency'].mean()
        # combine pass/fail counts  and average latency into a single DataFrame
        performance_df = pass_fail_counts[['pass', 'fail', 'total', 'pass_rate']].join(avg_latency.rename('average_latency'))
        performance_df = performance_df.reset_index()
        performance_df = performance_df.rename(columns={
            'ground_truth': 'Intent',
            'pass': 'Pass Count',
            'fail': 'Fail Count',
            'total': 'Total Count',
            'pass_rate': 'Pass Rate (%)',
            'average_latency': 'Average Latency (s)'
        })
        # sort by pass rate
        performance_df = performance_df.sort_values(by='Pass Rate (%)', ascending=False)
        print(performance_df.to_string(index=False))

    def clu_performance_breakdown(self) -> None:
        """
        Bar chart of pass/fail rate for all intends 
        """
        # get pass/fail counts and normalise to percentage
        pass_fail_counts = self.results_df.groupby('ground_truth')['f1_result'].value_counts().unstack(fill_value=0)
        pass_fail_counts = pass_fail_counts.div(pass_fail_counts.sum(axis=1), axis=0) * 100
        # bar chart
        plt.figure(figsize=(12, 6))
        pass_fail_counts.plot(kind='bar', stacked=True, color=['red', 'green'], ax=plt.gca())
        plt.title('Pass/Fail Rate for Each Intent')
        plt.xlabel('Intent')
        plt.ylabel('Percentage (%)')
        plt.xticks(rotation=45)
        plt.legend(title='Result', labels=['Fail', 'Pass'])
        plt.text(0, -1.2, f'Number of samples: {len(self.results_df["query"])}', ha='center', fontsize=12, color='black')
    
    def clu_performance_breakdown_old(self) -> None:
        """
        Bar chart of pass/fail rate for all intends for old CLU results (no answer length and latency metrics)
        """
        # get pass/fail counts
        pass_fail_counts = self.results_df_old.groupby('ground_truth')['f1_result'].value_counts().unstack(fill_value=0)
        # normalise to percentage
        pass_fail_counts = pass_fail_counts.div(pass_fail_counts.sum(axis=1), axis=0) * 100
        # bar chart
        plt.figure(figsize=(12, 6))
        pass_fail_counts.plot(kind='bar', stacked=True, color=['red', 'green'], ax=plt.gca())
        plt.title('Pass/Fail Rate for Each Intent (Old CLU Results)')
        plt.xlabel('Intent')
        plt.ylabel('Percentage (%)')
        plt.xticks(rotation=45)
        plt.legend(title='Result', labels=['Fail', 'Pass'])
        plt.tight_layout()
        plt.savefig(f"{self.clu_figure_filename_st}_performance_breakdown_old.png")
    
    def clu_aggregate_comparison(self) -> None:
        """
        Aggregate comparisons of old and new CLU results.

        1. Overal Accuracy Old vs Overall Accuracy New.
        2. Overall Info Accuracy Old (AdminInfo, CampusInfo) vs Overall Info Accuracy New (Info)
        3. Overall Feedback Accuracy Old vs Overall Feedback Accuracy New.
        """
        # calculate overall accuracy for old and new results
        old_accuracy = (self.results_df_old['f1_result'] == 'pass').mean() * 100
        new_accuracy = (self.results_df['f1_result'] == 'pass').mean() * 100
        # calculate overall info accuracy for old and new results
        old_info_accuracy = (self.results_df_old[self.results_df_old['ground_truth'].isin(['AdminInfo', 'CampusInfo'])]['f1_result'] == 'pass').mean() * 100
        new_info_accuracy = (self.results_df[self.results_df['ground_truth'] == 'Info']['f1_result'] == 'pass').mean() * 100
        # calculate overall feedback accuracy for old and new results
        old_feedback_accuracy = (self.results_df_old[self.results_df_old['ground_truth'] == 'Feedback']['f1_result'] == 'pass').mean() * 100
        new_feedback_accuracy = (self.results_df[self.results_df['ground_truth'] == 'Feedback']['f1_result'] == 'pass').mean() * 100

        print(f"Old CLU Overall Accuracy: {old_accuracy:.2f}%"
              f"\nNew CLU Overall Accuracy: {new_accuracy:.2f}%"
              f"\nOld CLU Info Accuracy: {old_info_accuracy:.2f}%"
              f"\nNew CLU Info Accuracy: {new_info_accuracy:.2f}%"
              f"\nOld CLU Feedback Accuracy: {old_feedback_accuracy:.2f}%"
              f"\nNew CLU Feedback Accuracy: {new_feedback_accuracy:.2f}%")

        categories = ['Overall Accuracy', 'Info Accuracy', 'Feedback Accuracy']
        old_scores = [old_accuracy, old_info_accuracy, old_feedback_accuracy]
        new_scores = [new_accuracy, new_info_accuracy, new_feedback_accuracy]
        x = range(len(categories))
        bar_width = 0.35

        # Use color palettes
        set2_palette = sns.color_palette("Set2", 2)
        plt.figure(figsize=(12, 6))
        plt.bar(x, old_scores, width=bar_width, label='Old CLU', color=set2_palette[0], alpha=0.7)
        plt.bar([i + bar_width for i in x], new_scores, width=bar_width, label='New CLU', color=set2_palette[1], alpha=0.7)
        #plt.title('CLU Aggregate Comparison', fontsize=18)
        plt.xlabel('Categories', fontsize=20)
        plt.ylabel('Accuracy (%)', fontsize=20)
        plt.xticks([i + bar_width / 2 for i in x], categories, fontsize=16)
        plt.legend(title='Model Version', fontsize=16)
        plt.ylim(0, 100)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{self.clu_figure_filename_st}_aggregate_comparison.png")


class CQAVis:
    def __init__(self) -> tuple[pd.DataFrame, dict]:
        """
        Preprocess results from a JSON file into a DataFrame and metrics dictionary.
        """
        self.cqa_figure_filename_st = FIG_PATHS["cqa"]  # start of filename for CQA figures
        eval_data_handler = EvalDataHandling()
        data = eval_data_handler.get_eval_results(RESULT_PATHS["cqa"])

        # convert metrics into a dict
        metrics = data.get('metrics', {})
        metrics['average_answer_length'], metrics['average_latency'] = calc_response_level_metrics(data)
        # convert results into a dataframe
        results_df = pd.DataFrame(data['rows'])
        # rename flattened keys to clean column names
        results_df = results_df.rename(columns={
            'inputs.query': 'query',
            'inputs.context': 'context',
            'inputs.response': 'response',
            'inputs.ground_truth': 'ground_truth',
            'inputs.answer_length': 'answer_length',
            'inputs.latency': 'latency',
            'outputs.f1_score.f1_score': 'f1_score',
            'outputs.f1_score.f1_result': 'f1_result',
            'outputs.f1_score.f1_threshold': 'f1_threshold'
        })
        
        self.results_df = results_df
        self.metrics = metrics

    def cqa_performance_breakdown(self) -> None:
        """
        Bar chart for total number of correct (passed) responses and total number of incorrect (failed) responses
        A label of average answer length and average latency is added to the chart.
        """
        pass_fail_counts = self.results_df['f1_result'].value_counts(normalize=True) * 100
        response_time = self.metrics.get('average_latency', 0)
        print(f"Pass/Fail Counts:\n{pass_fail_counts}")
        print(f"Average Latency: {response_time:.2f}s")
        plt.figure(figsize=(8, 6))
        sns.barplot(x=pass_fail_counts.index, y=pass_fail_counts.values, palette=['green', 'red'], legend=False)
        plt.title(f'CQA Performance Breakdown\nlatency: {self.metrics["average_latency"]:.2f}s, answer length: {self.metrics["average_answer_length"]:.2f} tokens')
        plt.xlabel('Result')
        plt.ylabel('Percentage (%)')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.cqa_figure_filename_st}_performance_breakdown.png")


class RAGVis:
    def __init__(self) -> tuple[pd.DataFrame, dict]:
        """
        Preprocess results from a JSON file into a DataFrame and metrics dictionary.
        """
        self.rag_figure_filename_st = FIG_PATHS["rag"]  # start of filename for RAG figures
        eval_data_handler = EvalDataHandling()

        # load all RAG results
        rag_all_types = ["main", "gpt4o", "gpt4o_mini", "phi4", "llama3-instruct", "phi4_mini_instruct",
                         "chunk_300", "chunk_1000", "chunk_2000",
                         "top_2", "top_5", "top_10"]
        all_data = {}
        for rag_type in rag_all_types:
            all_data[rag_type] = eval_data_handler.get_eval_results(RESULT_PATHS["rag_all"][rag_type])

        # convert metrics into a dict
        all_metrics = {}
        for key in all_data:
            all_metrics[key] = all_data[key].get('metrics', {})
            all_metrics[key]["average_answer_length"], all_data[key]['metrics']['average_latency'] = calc_response_level_metrics(all_data[key])
        # convert results into a dataframe
        all_results = {}
        for key in all_data:
            all_results[key] = {}
            all_results[key]['rows'] = pd.DataFrame(all_data[key]['rows'])
            # rename flattened keys to clean column names
            all_results[key]['rows'] = all_results[key]['rows'].rename(columns={
                'inputs.query': 'query',
                'inputs.context': 'context',
                'inputs.response': 'response',
                'inputs.answer_length': 'answer_length',
                'inputs.latency': 'latency',
                'outputs.retrieval.retrieval_result': 'retrieval_result',
                'outputs.retrieval.retrieval_threshold': 'retrieval_threshold',
                'outputs.grounding.groundedness': 'groundedness',
                'outputs.grounding.gpt_groundedness': 'gpt_groundedness',
                'outputs.grounding.groundedness_reason': 'groundedness_reason',
                'outputs.grounding.groundedness_result': 'groundedness_result',
                'outputs.grounding.groundedness_threshold': 'groundedness_threshold',
                'outputs.relevance.relevance': 'relevance',
                'outputs.relevance.gpt_relevance': 'gpt_relevance',
                'outputs.relevance.relevance_reason': 'relevance_reason',
                'outputs.relevance.relevance_result': 'relevance_result',
                'outputs.relevance.relevance_threshold': 'relevance_threshold'
            })
        self.all_results = all_results
        self.all_metrics = all_metrics
        
    
    def rag_performance_breakdown(self) -> None:
        """
        bar chart for all metrics (retrieval, grounding, relevance) out of 5.
        """
        retrieval_score = self.all_metrics["main"].get('retrieval.retrieval', 0)
        grounding_score = self.all_metrics["main"].get('grounding.groundedness', 0)
        relevance_score = self.all_metrics["main"].get('relevance.relevance', 0)
        scores = {
            'Retrieval': retrieval_score,
            'Grounding': grounding_score,
            'Relevance': relevance_score
        }
        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(scores.keys()), y=list(scores.values()), palette='viridis')
        plt.title(f'RAG Performance Breakdown\nlatency: {self.metrics["average_latency"]:.2f}s, answer length: {self.metrics["average_answer_length"]:.2f} tokens')
        plt.xlabel('Metrics')
        plt.ylabel('Score (out of 5)')
        plt.ylim(0, 5)
        for i, score in enumerate(scores.values()):
            plt.text(i, score + 0.1, f"{score:.1f}", ha='center', va='bottom', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{self.rag_figure_filename_st}_performance_breakdown.png")
    
    def rag_model_comparison_table(self) -> None:
        model_types = ['gpt4o', 'gpt4o_mini', 'phi4', "llama3-instruct", "phi4_mini_instruct"]
        model_scores = {}
        for model_type in model_types:
            retrieval_score = self.all_metrics[model_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[model_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[model_type].get('relevance.relevance', 0)
            response_length = self.all_metrics[model_type].get('average_answer_length', 0)
            response_time = self.all_metrics[model_type].get('average_latency', 0)
            model_scores[model_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for model-based performance
        model_performance_df = pd.DataFrame({
            'Model': model_types,
            'Retrieval': [model_scores[model]['Retrieval'] for model in model_types],
            'Grounding': [model_scores[model]['Grounding'] for model in model_types],
            'Relevance': [model_scores[model]['Relevance'] for model in model_types],
            'Length (w)': [model_scores[model]['Length (w)'] for model in model_types],
            'Time (s)': [model_scores[model]['Time (s)'] for model in model_types]
        })
        print("Model-Based Performance Data:"
              f"\n{model_performance_df.to_string(index=False)}")

    def rag_chunk_comparison_table(self) -> None:
        """
        Chunk-based performance breakdown for different chunk sizes (300, 1000, 2000).
        """
        chunk_types = ['chunk_300', 'chunk_1000', 'chunk_2000']
        chunk_scores = {}
        for chunk_type in chunk_types:
            retrieval_score = self.all_metrics[chunk_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[chunk_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[chunk_type].get('relevance.relevance', 0)
            response_length = self.all_metrics[chunk_type].get('average_answer_length', 0)
            response_time = self.all_metrics[chunk_type].get('average_latency', 0)
            chunk_scores[chunk_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }

        # Create a DataFrame for chunk-based performance
        chunk_performance_df = pd.DataFrame({
            'Chunk Size': ['Small (300)', 'Medium (1000)', 'Large (2000)'],
            'Retrieval': [chunk_scores[chunk]['Retrieval'] for chunk in chunk_types],
            'Grounding': [chunk_scores[chunk]['Grounding'] for chunk in chunk_types],
            'Relevance': [chunk_scores[chunk]['Relevance'] for chunk in chunk_types],
            'Length (w)': [chunk_scores[chunk]['Length (w)'] for chunk in chunk_types],
            'Time (s)': [chunk_scores[chunk]['Time (s)'] for chunk in chunk_types]
        })
        print("Chunk-Based Performance Data:"
              f"\n{chunk_performance_df.to_string(index=False)}")
    
    def rag_top_n_comparison_table(self) -> None:
        """
        Top N performance breakdown for different top N values (5, 10, 20).
        """
        top_n_types = ['top_2', 'top_5', 'top_10']
        top_n_scores = {}
        for top_n_type in top_n_types:
            retrieval_score = self.all_metrics[top_n_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[top_n_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[top_n_type].get('relevance.relevance', 0)
            response_length = self.all_metrics[top_n_type].get('average_answer_length', 0)
            response_time = self.all_metrics[top_n_type].get('average_latency', 0)
            top_n_scores[top_n_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }

        # Create a DataFrame for top N performance
        top_n_performance_df = pd.DataFrame({
            'Top N': ['Top 3', 'Top 5', 'Top 10'],
            'Retrieval': [top_n_scores[top]['Retrieval'] for top in top_n_types],
            'Grounding': [top_n_scores[top]['Grounding'] for top in top_n_types],
            'Relevance': [top_n_scores[top]['Relevance'] for top in top_n_types],
            'Length (w)': [top_n_scores[top]['Length (w)'] for top in top_n_types],
            'Time (s)': [top_n_scores[top]['Time (s)'] for top in top_n_types]
        })
        print("Top N Performance Data:"
              f"\n{top_n_performance_df.to_string(index=False)}")
 
    def rag_combined_performance_breakdown(self) -> None:
        """
        Combined performance breakdown for RAG (retrieval, grounding, relevance) with variations in model and chunking strategy.
        Note: embedding mode is text-embedding-ada-002, hybrid RAG: vector and keyword search.

        Variations in model (GPT-4o, GPT-4o mini, Llama3-Instruct, Phi-4, Phi-4 Mini Instruct).
        Variation in chunking strategy (chunk size: small 300, medium 1000, large 2000).

        Clustered Bar Chart for Model-Based and Chunk-Based Performance Breakdown.
        You could use a Line Chart to plot the Time (s) and Answer Length across the different chunk sizes for each model. This would clearly show how these two metrics are affected by the chunking strategy and model choice, providing a more complete picture of your evaluation.
        """
        # Calculate average Time (s) and answer length for each model and chunk size
        model_types = ['gpt4o', 'gpt4o_mini', 'phi4', "llama3-instruct", "phi4_mini_instruct"]
        chunk_types = ['chunk_300', 'chunk_1000', 'chunk_2000']
        top_n_types = ['top_2', 'top_5', 'top_10']
        model_scores = {}
        for model_type in model_types:
            retrieval_score = self.all_metrics[model_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[model_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[model_type].get('relevance.relevance', 0)
            model_scores[model_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
            }
        chunk_scores = {}
        for chunk_type in chunk_types:
            retrieval_score = self.all_metrics[chunk_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[chunk_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[chunk_type].get('relevance.relevance', 0)
            chunk_scores[chunk_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
            }
        top_n_scores = {}
        for top_n_type in top_n_types:
            retrieval_score = self.all_metrics[top_n_type].get('retrieval.retrieval', 0)
            grounding_score = self.all_metrics[top_n_type].get('grounding.groundedness', 0)
            relevance_score = self.all_metrics[top_n_type].get('relevance.relevance', 0)
            top_n_scores[top_n_type] = {
                'Retrieval': retrieval_score,
                'Grounding': grounding_score,
                'Relevance': relevance_score,
            }
        
        # create a Clustered Bar Chart for Model-Based and Chunk-Based Performance Breakdown
        model_df = pd.DataFrame({
            'Model': model_types,
            'Retrieval': [model_scores[model]['Retrieval'] for model in model_types],
            'Grounding': [model_scores[model]['Grounding'] for model in model_types],
            'Relevance': [model_scores[model]['Relevance'] for model in model_types],
        })
        chunk_df = pd.DataFrame({
            'Chunk Size': ['Small (300)', 'Medium (1000)', 'Large (2000)'],
            'Retrieval': [chunk_scores[chunk]['Retrieval'] for chunk in chunk_types],
            'Grounding': [chunk_scores[chunk]['Grounding'] for chunk in chunk_types],
            'Relevance': [chunk_scores[chunk]['Relevance'] for chunk in chunk_types],
        })
        top_n_df = pd.DataFrame({
            'Top N': ['Top 2', 'Top 5', 'Top 10'],
            'Retrieval': [top_n_scores[top]['Retrieval'] for top in top_n_types],
            'Grounding': [top_n_scores[top]['Grounding'] for top in top_n_types],
            'Relevance': [top_n_scores[top]['Relevance'] for top in top_n_types],
        })

        # Melt the DataFrames for seaborn
        model_melted = model_df.melt(id_vars='Model', var_name='Metric', value_name='Score')
        chunk_melted = chunk_df.melt(id_vars='Chunk Size', var_name='Metric', value_name='Score')
        top_n_melted = top_n_df.melt(id_vars='Top N', var_name='Metric', value_name='Score')
        # Create the figure and axes
        fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
        # Plot for model-based performance
        sns.barplot(data=model_melted, x='Model', y='Score', hue='Metric', ax=axes[0], palette='viridis')
        axes[0].set_title('RAG Model-Based Performance Breakdown')
        axes[0].set_xlabel('Model')
        axes[0].set_ylabel('Score (out of 5)')
        axes[0].set_ylim(0, 5)
        axes[0].legend(title='Metric')
        # Plot for chunk-based performance
        sns.barplot(data=chunk_melted, x='Chunk Size', y='Score', hue='Metric', ax=axes[1], palette='viridis')
        axes[1].set_title('RAG Chunk-Based Performance Breakdown')
        axes[1].set_xlabel('Chunk Size')
        axes[1].set_ylabel('Score (out of 5)')
        axes[1].set_ylim(0, 5)
        axes[1].legend(title='Metric')
        # Plot for top N performance
        sns.barplot(data=top_n_melted, x='Top N', y='Score', hue='Metric', ax=axes[2], palette='viridis')
        axes[2].set_title('RAG Top N Performance Breakdown')
        axes[2].set_xlabel('Top N')
        axes[2].set_ylabel('Score (out of 5)')
        axes[2].set_ylim(0, 5)
        axes[2].legend(title='Metric')
        # Adjust layout
        fig.autofmt_xdate()
        plt.tight_layout()
        # Save the figure
        plt.savefig(f"{self.rag_figure_filename_st}_combined_performance_breakdown.png")

    def rag_model_bubble_plot(self) -> None:
        """
        Bubble plot color:model, bubble-size: average performnace (retrieval, grounding, relevance), x: response time, y: response length
        """
        models = ['gpt4o', 'gpt4o_mini', 'phi4', "llama3-instruct", "phi4_mini_instruct"]
        model_names = ["GPT-4o", "GPT-4o Mini", "Phi-4", "Llama3-Instruct", "Phi-4 Mini Instruct"]
        colors = sns.color_palette("Set2", len(models))
        model_data = []
        for idx, model in enumerate(models):
            avg_performance = (self.all_metrics[model].get('retrieval.retrieval', 0) +
                   self.all_metrics[model].get('grounding.groundedness', 0) +
                   self.all_metrics[model].get('relevance.relevance', 0)) / 3
            response_time = self.all_metrics[model].get('average_latency', 0)
            response_length = self.all_metrics[model].get('average_answer_length', 0)
            model_data.append({
            'Model': model_names[idx],
            'Avg Performance': avg_performance,
            'Response Time': response_time,
            'Response Length': response_length,
            'Color': colors[idx]
            })
        model_df = pd.DataFrame(model_data)
        plt.figure(figsize=(10, 8))
        for i, row in model_df.iterrows():
            plt.scatter(
            row['Response Time'],
            row['Response Length'],
            s=row['Avg Performance']**4 * 100,
            color=row['Color'],
            alpha=0.6,
            edgecolors='w',
            linewidth=1,
            )
        # Custom legend: only color designations, not bubble sizes
        legend_handles = [
            plt.Line2D([0], [0], marker='o', color='w', label=model_names[i],
                   markerfacecolor=colors[i], markersize=12)
            for i in range(len(models))
        ]
        plt.legend(handles=legend_handles, title="Model", loc="best", fontsize=16)
        #plt.title('Model-based Comparison for RAG')
        plt.xlabel('Average Response Time (s)', fontsize=20)
        plt.ylabel('Average Response Length (tokens)', fontsize=20)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{self.rag_figure_filename_st}_model_bubble_plot.png")

    def rag_chunk_radar(self) -> None:
        """
        Radar Chart for retrieval, grounding, relevance, response time based on chunk size (300, 1000, 2000).
        """
        chunk_sizes = ['chunk_300', 'chunk_1000', 'chunk_2000']
        chunk_labels = ['Small (300)', 'Medium (1000)', 'Large (2000)']
        metrics = ['Retrieval', 'Grounding', 'Relevance', 'Response Time']
        chunk_data = []
        for chunk in chunk_sizes:
            retrieval = self.all_metrics[chunk].get('retrieval.retrieval', 0)
            grounding = self.all_metrics[chunk].get('grounding.groundedness', 0)
            relevance = self.all_metrics[chunk].get('relevance.relevance', 0)
            response_time = self.all_metrics[chunk].get('average_latency', 0)
            chunk_data.append([retrieval, grounding, relevance, response_time])
        chunk_data = np.array(chunk_data)
        # Radar chart setup
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        chunk_data = np.concatenate((chunk_data, chunk_data[:, [0]]), axis=1)
        angles += angles[:1]
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        for i, chunk in enumerate(chunk_data):
            ax.plot(angles, chunk, label=chunk_labels[i])
            ax.fill(angles, chunk, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'])
        ax.set_ylim(0, 5)
        plt.title('RAG Chunk Size Comparison', size=20, y=1.05)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        plt.savefig(f"{self.rag_figure_filename_st}_chunk_radar.png")

    def rag_scatter_top_n(self) -> None:
        """
        Dual-Axis Chart: bar chart for relevance score, line chart for response time based on top N (2, 5, 10).
        Uses the same color palette as rag_model_bubble_plot.
        """
        top_n_types = ['top_2', 'top_5', 'top_10']
        top_n_labels = ['Top 2', 'Top 5', 'Top 10']
        palette = sns.color_palette("Set2", len(top_n_types))
        relevance_scores = []
        response_times = []
        for top_n in top_n_types:
            relevance = self.all_metrics[top_n].get('relevance.relevance', 0)
            response_time = self.all_metrics[top_n].get('average_latency', 0)
            relevance_scores.append(relevance)
            response_times.append(response_time)
        x = np.arange(len(top_n_labels))
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.set_xlabel('Top N')
        # font size = 14
        ax1.set_ylabel('Relevance Score', color=palette[0], fontweight='bold', fontsize=14)
        bars = ax1.bar(x, relevance_scores, color=palette, alpha=0.6)
        ax1.tick_params(axis='y', labelcolor=palette[0])
        ax2 = ax1.twinx()
        ax2.set_ylabel('Response Time (s)', color=palette[2], fontweight='bold', fontsize=14)
        ax2.plot(x, response_times, color=palette[2], marker='o')
        ax2.tick_params(axis='y', labelcolor=palette[2])
        plt.xticks(x, top_n_labels)
        plt.title('RAG Top N Comparison')
        fig.tight_layout()
        plt.savefig(f"{self.rag_figure_filename_st}_scatter_top_n.png")


class AgentVis:
    def __init__(self, agent_name: str = "CampusInfo"):
        """
        Preprocess results from a JSON file into a DataFrame and metrics dictionary.
        """
        self.agent_name = agent_name
        self.agent_figure_filename_st = FIG_PATHS[agent_name.lower()]
        eval_data_handler = EvalDataHandling()
        all_result_types = ["gpt4o", "gpt4o_mini", "llama3-instruct", "phi4_mini_instruct",
                            "no_examples", "simple_examples", "react_examples",
                            "single_utterance_queries", "multi_utterance_queries"]

        # load all agentic results for this agent
        all_data = {}
        for result_type in all_result_types:
            all_data[result_type] = eval_data_handler.get_eval_results(RESULT_PATHS[agent_name.lower() + "_all"][result_type])
        
        # convert metrics into a dict
        all_metrics = {}
        for key in all_data:
            all_metrics[key] = all_data[key].get('metrics', {})
            all_metrics[key]["average_answer_length"], all_data[key]['metrics']['average_latency'] = calc_response_level_metrics(all_data[key])
        # convert results into a dataframe
        all_results = {}
        for key in all_data:
            all_results[key] = {}
            all_results[key]['rows'] = pd.DataFrame(all_data[key]['rows'])
            # rename flattened keys to clean column names
            all_results[key]['rows'] = all_results[key]['rows'].rename(columns={
                'inputs.query': 'query',
                'inputs.context': 'context',
                'inputs.response': 'response',
                'inputs.ground_truth': 'ground_truth',
                'inputs.answer_length': 'answer_length',
                'inputs.latency': 'latency',
                'outputs.intend_resolution.intent_resolution': 'intent_resolution',
                'outputs.intend_resolution.intent_resolution_threshold': 'intent_resolution_threshold',
                #'outputs.tool_call_accuracy.tool_call_accuracy': 'tool_call_accuracy',
                #'outputs.tool_call_accuracy.tool_call_accuracy_threshold': 'tool_call_accuracy_threshold',
                'outputs.task_adherence.task_adherence': 'task_adherence',
                'outputs.task_adherence.task_adherence_threshold': 'task_adherence_threshold',
                'outputs.relevance.relevance': 'relevance',
                'outputs.relevance.gpt_relevance': 'gpt_relevance',
                'outputs.relevance.relevance_threshold': 'relevance_threshold',
                'outputs.coherence.coherence': 'coherence',
                'outputs.coherence.gpt_coherence': 'gpt_coherence',
                'outputs.coherence.coherence_threshold': 'coherence_threshold',
                'outputs.fluency.fluency': 'fluency',
                'outputs.fluency.gpt_fluency': 'gpt_fluency',
                'outputs.fluency.fluency_threshold': 'fluency_threshold'
            })
        self.all_results = all_results
        self.all_metrics = all_metrics

    def agent_performance_breakdown(self) -> None:
        """
        Bar chart for all metrics (intent resolution, tool call accuracy, task adherence) out of 5.
        """
        result_type = "gpt4o"
        intent_resolution_score = self.all_metrics[result_type].get('intend_resolution.intent_resolution', 0)
        #tool_call_accuracy_score = self.all_metrics["gpt4o"].get('tool_call_accuracy.tool_call_accuracy', 0)
        task_adherence_score = self.all_metrics[result_type].get('task_adherence.task_adherence', 0)
        relevance_score = self.all_metrics[result_type].get('relevance.relevance', 0)
        coherence_score = self.all_metrics[result_type].get('coherence.coherence', 0)
        fluency_score = self.all_metrics[result_type].get('fluency.fluency', 0)
        scores = {
            'Intent Resolution': intent_resolution_score,
            #'Tool Call Accuracy': tool_call_accuracy_score,
            'Task Adherence': task_adherence_score,
            'Relevance': relevance_score,
            'Coherence': coherence_score,
            'Fluency': fluency_score
        }
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(scores.keys()), y=list(scores.values()), palette='viridis')
        plt.title(f'{self.agent_name} Agent Performance Breakdown\nlatency: {self.all_metrics[result_type]["average_latency"]:.2f}s, answer length: {self.all_metrics[result_type]["average_answer_length"]:.2f} tokens')
        plt.xlabel('Metrics')
        plt.ylabel('Score (out of 5)')
        plt.ylim(0, 5)
        
        for i, score in enumerate(scores.values()):
            plt.text(i, score + 0.1, f"{score:.1f}", ha='center', va='bottom', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(f"{self.agent_figure_filename_st}_performance_breakdown.png")
        
    def agent_model_comparison_table(self) -> None:
        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        model_scores = {}
        for model_type in model_types:
            intent_resolution_score = self.all_metrics[model_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[model_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[model_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[model_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[model_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[model_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[model_type].get('average_answer_length', 0)
            response_time = self.all_metrics[model_type].get('average_latency', 0)
            model_scores[model_type] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for model-based performance
        model_performance_df = pd.DataFrame({ # limit values to 2 decimal places
            'Model': model_types,
            'Intent Resolution': [round(model_scores[model]['Intent Resolution'], 2) for model in model_types],
            #'Tool Call Accuracy': [round(model_scores[model]['Tool Call Accuracy'], 2) for model in model_types],
            'Task Adherence': [round(model_scores[model]['Task Adherence'], 2) for model in model_types],
            'Relevance': [round(model_scores[model]['Relevance'], 2) for model in model_types],
            'Coherence': [round(model_scores[model]['Coherence'], 2) for model in model_types],
            'Fluency': [round(model_scores[model]['Fluency'], 2) for model in model_types],
            'Length (w)': [round(model_scores[model]['Length (w)'], 2) for model in model_types],
            'Time (s)': [round(model_scores[model]['Time (s)'], 2) for model in model_types]
        })
        print(f"{self.agent_name} Model-Based Performance Data:"
                f"\n{model_performance_df.to_string(index=False)}")

    def agent_prompting_strategy_comparison_table(self) -> None:
        """
        Compare the performance of different few-shot prompting strategies for the agent.
        """
        few_shot_methods = ["no_examples", "simple_examples", "react_examples"]
        few_shot_scores = {}
        for few_shot_method in few_shot_methods:
            intent_resolution_score = self.all_metrics[few_shot_method].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[few_shot_method].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[few_shot_method].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[few_shot_method].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[few_shot_method].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[few_shot_method].get('fluency.fluency', 0)
            response_length = self.all_metrics[few_shot_method].get('average_answer_length', 0)
            response_time = self.all_metrics[few_shot_method].get('average_latency', 0)
            few_shot_scores[few_shot_method] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for few-shot prompting strategy performance
        few_shot_performance_df = pd.DataFrame({
            'Prompting': few_shot_methods,
            'Intent Resolution': [round(few_shot_scores[method]['Intent Resolution'], 2) for method in few_shot_methods],
            #'Tool Call Accuracy': [round(few_shot_scores[method]['Tool Call Accuracy'], 2) for method in few_shot_methods],
            'Task Adherence': [round(few_shot_scores[method]['Task Adherence'], 2) for method in few_shot_methods],
            'Relevance': [round(few_shot_scores[method]['Relevance'], 2) for method in few_shot_methods],
            'Coherence': [round(few_shot_scores[method]['Coherence'], 2) for method in few_shot_methods],
            'Fluency': [round(few_shot_scores[method]['Fluency'], 2) for method in few_shot_methods],
            'Length (w)': [round(few_shot_scores[method]['Length (w)'], 2) for method in few_shot_methods],
            'Time (s)': [round(few_shot_scores[method]['Time (s)'], 2) for method in few_shot_methods]
        })
        print(f"{self.agent_name} Few-Shot Prompting Strategy Performance Data:"
                f"\n{few_shot_performance_df.to_string(index=False)}")
    
    def agent_query_type_comparison_table(self) -> None:
        """
        Compare the performance of different query types for the agent.
        1. Single-Utterance Queries
        2. Multi-Utterance Queries
        """
        query_types = ["single_utterance_queries", "multi_utterance_queries"]
        query_type_scores = {}
        for query_type in query_types:
            intent_resolution_score = self.all_metrics[query_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[query_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[query_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[query_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[query_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[query_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[query_type].get('average_answer_length', 0)
            response_time = self.all_metrics[query_type].get('average_latency', 0)
            query_type_scores[query_type] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for query type performance
        query_type_performance_df = pd.DataFrame({
            'Query Type': ['Single-Utterance', 'Multi-Utterance'],
            'Intent Resolution': [round(query_type_scores[qtype]['Intent Resolution'], 2) for qtype in query_types],
            #'Tool Call Accuracy': [round(query_type_scores[qtype]['Tool Call Accuracy'], 2) for qtype in query_types],
            'Task Adherence': [round(query_type_scores[qtype]['Task Adherence'], 2) for qtype in query_types],
            'Relevance': [round(query_type_scores[qtype]['Relevance'], 2) for qtype in query_types],
            'Coherence': [round(query_type_scores[qtype]['Coherence'], 2) for qtype in query_types],
            'Fluency': [round(query_type_scores[qtype]['Fluency'], 2) for qtype in query_types],
            'Length (w)': [round(query_type_scores[qtype]['Length (w)'], 2) for qtype in query_types],
            'Time (s)': [round(query_type_scores[qtype]['Time (s)'], 2) for qtype in query_types]
        })
        print(f"{self.agent_name} Query Type Performance Data:"
                f"\n{query_type_performance_df.to_string(index=False)}")


class CombinedAgentVis:
    def __init__(self, agent_names: List[str] = ["CampusInfo", "AdminInfo", "Feedbac", "ChartPlotter"]):
        AgentVis_list = [AgentVis(agent_name) for agent_name in agent_names]
        self.agent_names = agent_names
        self.combined_figure_filename_st = FIG_PATHS["combined_agents"]

    def combined_aggregated_performance(self) -> None:
        """
        Aggregated performance for each agent per evaluated models, prompting strategies, and query types.
        Aggregation includes agentic metrics only: intent resolution, task adherence, relevance, coherence, fluency.
        """
        # aggregate agentic performance for each agent and (model, prompting strategy, query type)
        eval_methods = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct', 'no_examples', 'simple_examples', 'react_examples', 'single_utterance_queries', 'multi_utterance_queries']
        all_agent_aggregated_scores = {}
        for agent_name in self.agent_names:
            agent_vis = AgentVis(agent_name)
            agent_aggregated_scores = {}
            for model_type in eval_methods:
                intent_resolution_score = agent_vis.all_metrics[model_type].get('intend_resolution.intent_resolution', 0)
                #tool_call_accuracy_score = agent_vis.all_metrics[model_type].get('tool_call_accuracy.tool_call_accuracy', 0)
                task_adherence_score = agent_vis.all_metrics[model_type].get('task_adherence.task_adherence', 0)
                relevance_score = agent_vis.all_metrics[model_type].get('relevance.relevance', 0)
                coherence_score = agent_vis.all_metrics[model_type].get('coherence.coherence', 0)
                fluency_score = agent_vis.all_metrics[model_type].get('fluency.fluency', 0)
                aggregated_score = (intent_resolution_score +
                                    task_adherence_score +
                                    relevance_score +
                                    coherence_score +
                                    fluency_score) / 5
                agent_aggregated_scores[model_type] = aggregated_score
            all_agent_aggregated_scores[agent_name] = agent_aggregated_scores
        # create a DataFrame for combined agent model comparison
        combined_data = []
        for agent_name, scores in all_agent_aggregated_scores.items():
            for model_type, aggregated_score in scores.items():
                combined_data.append({
                    'Agent': agent_name,
                    'Method': model_type,
                    'Aggregated Score': aggregated_score
                })
        combined_df = pd.DataFrame(combined_data)
        print(combined_df)

    def combined_grouped_box_plots(self) -> None:
        """
        Generates grouped box plots for response time only, grouped by agent names.
        - Each group (x-axis) is an agent: CampusInfo, AdminInfo, Feedback, ChartPlotter.
        - Within each agent's group, box plots are shown for each model: gpt4o, gpt4o_mini, llama3-instruct, phi4_mini_instruct.
        - This visualizes the distribution of response time for each agent, broken down by model.
        """

        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        all_agent_data = {}
        for agent_name in self.agent_names:
            agent_vis = AgentVis(agent_name)
            agent_data = []
            for model_type in model_types:
                df = agent_vis.all_results[model_type]['rows']
                for _, row in df.iterrows():
                    agent_data.append({
                        'Model': model_type,
                        'Response Length': row['answer_length'],
                        'Response Time': row['latency']
                    })
            all_agent_data[agent_name] = pd.DataFrame(agent_data)
        print(all_agent_data)
        # remove extreme outliers (response time > 60s)
        for agent_name in self.agent_names:
            all_agent_data[agent_name] = all_agent_data[agent_name][all_agent_data[agent_name]["Response Time"] <= 60]

        # created grouped box plots for response time for each agent
        sns.boxplot(x="Agent", y="Response Time", hue="Model",
                data=pd.concat([all_agent_data[agent_name].assign(Agent=agent_name) for agent_name in self.agent_names]),
                palette="Set2")
        plt.title('Response Time Distribution by Agent and Model')
        plt.xlabel('Agent')
        plt.ylabel('Response Time (s)')
        plt.legend(title='Model')
        plt.tight_layout()
        plt.savefig(f"{self.combined_figure_filename_st}_grouped_box_plots_response_time.png")

        # created gruped box plots for response length for each agent
        # sns.boxplot(x="Agent", y="Response Length", hue="Model",
        #         data=pd.concat([all_agent_data[agent_name].assign(Agent=agent_name) for agent_name in self.agent_names]),
        #         palette="Set2")
        # plt.title('Response Length Distribution by Agent and Model')
        # plt.xlabel('Agent')
        # plt.ylabel('Response Length (words)')
        # plt.legend(title='Model')
        # plt.tight_layout()
        # plt.savefig(f"{self.combined_figure_filename_st}_grouped_box_plots_response_length.png")

    def combined_prompting_diverging_bar_chart(self) -> None:
        """
        Diverging Bar Chart
        Show difference (ReAct – Few-Shot) in response length.
        Positive values → longer responses, negative values → shorter responses.
        Use case: Highlights direction and magnitude of effect quickly.
        """

        few_shot_methods = ["simple_examples", "react_examples"]
        response_length_per_agent = {}
        for agent_name in self.agent_names:
            agent_vis = AgentVis(agent_name)
            agent_response_lengths = {}
            for few_shot_method in few_shot_methods:
                response_length = agent_vis.all_metrics[few_shot_method].get('average_answer_length', 0)
                agent_response_lengths[few_shot_method] = response_length
            response_length_per_agent[agent_name] = agent_response_lengths

        # calculate difference (ReAct - Few-Shot)
        response_length_diff = {}
        for agent_name, lengths in response_length_per_agent.items():
            diff = lengths["react_examples"] - lengths["simple_examples"]
            response_length_diff[agent_name] = diff
        # create diverging bar chart
        plt.figure(figsize=(10, 6))
        # use color palette seaborn Set2
        colors = sns.color_palette("Set2", len(response_length_diff))
        bars = plt.bar(response_length_diff.keys(), response_length_diff.values(), color=colors, alpha=0.6)
        plt.axhline(0, color='black', linewidth=0.8)
        plt.title('Difference in Response Length (ReAct - Few-Shot) by Agent')
        plt.xlabel('Agent')
        plt.ylabel('Difference in Response Length (words)')
        for i, val in enumerate(response_length_diff.values()):
            plt.text(i, val + (0.5 if val >= 0 else -0.5), f"{val:.1f}", ha='center', va='bottom' if val >= 0 else 'top', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{self.combined_figure_filename_st}_diverging_bar_chart_response_length.png")
    
    def combined_prompting_diverging_bar_chart_horizontal(self) -> None:
        """
        Diverging Bar Chart
        How ReAct (Few-Shot) Affects Response Length by Agent.
        Positive values → longer responses, negative values → shorter responses.

        Flip bars horizontally (agents on the y-axis). Readers scan names easier and compare lengths more intuitively.  
        Increase bar thickness slightly: makes differences more noticeable.
        Annotate the axis zero line clearly (e.g., “No difference”) to reinforce the reference point.
        Add % differences alongside raw word counts, or show both with a dual axis or tooltip.
        Use a diverging color palette: Make positive values shades of green/blue and negative values shades of red/orange. This instantly conveys “increase” vs. “decrease.”
        """

        few_shot_methods = ["simple_examples", "react_examples"]
        response_length_per_agent = {}
        for agent_name in self.agent_names:
            agent_vis = AgentVis(agent_name)
            agent_response_lengths = {}
            for few_shot_method in few_shot_methods:
                response_length = agent_vis.all_metrics[few_shot_method].get('average_answer_length', 0)
                agent_response_lengths[few_shot_method] = response_length
            response_length_per_agent[agent_name] = agent_response_lengths

        # calculate difference (ReAct - Few-Shot)
        response_length_diff = {}
        percent_diff = {}
        for agent_name, lengths in response_length_per_agent.items():
            base = lengths["simple_examples"]
            diff = lengths["react_examples"] - base
            response_length_diff[agent_name] = diff
            # avoid division by zero
            percent_diff[agent_name] = (diff / base * 100) if base != 0 else 0

        # create diverging bar chart
        plt.figure(figsize=(10, 6))

        # diverging color palette: positive = blue/green, negative = red/orange
        colors = [
            '#2ca02c' if val >= 0 else '#d62728'  # green for increase, red for decrease
            for val in response_length_diff.values()
        ]

        # thicker bars (height increased)
        bars = plt.barh(
            list(response_length_diff.keys()),
            list(response_length_diff.values()),
            color=colors,
            alpha=0.7,
            height=0.7  # increased from 0.5
        )

        # zero line with annotation
        plt.axvline(0, color='black', linewidth=1)
        plt.title('How ReAct (Few-Shot) Affects Response Length by Agent')
        plt.ylabel('Agent')
        plt.xlabel('Difference in Response Length (words)')

        # annotate bars with raw + % difference
        for i, (agent, val) in enumerate(response_length_diff.items()):
            pct = percent_diff[agent]
            text = f"{pct:+.1f}%"
            
            # Set a margin based on bar length
            margin = max(abs(val) * 0.02, 6)  # at least 3 units away, scaled with val
            plt.text(val + margin, i, text, va='center', ha='right', weight="bold", fontsize=11)

        plt.tight_layout()
        plt.savefig(f"{self.combined_figure_filename_st}_diverging_bar_chart_response_length_horizontal.png")



class EndToEndVis:
    """
    End-to-End system orchestration visualization and analysis.
    """

    def __init__(self) -> None:
        """
        Preprocess results from a JSON file into a DataFrame and metrics dictionary.
        """
        self.name = "EndToEnd"
        self.figure_filename_st = FIG_PATHS[self.name.lower()]  # start of filename for end-to-end figures
        eval_data_handler = EvalDataHandling()
        all_result_types = ["gpt4o", "llama3-instruct", "gpt4o_mini", "phi4_mini_instruct",
                            "no_clu", "no_triage", "no_cqa", "no_rag",
                            "single_utterance_queries", "multi_utterance_queries"]
    
        # load all end-to-end results
        all_data = {}
        for result_type in all_result_types:
            all_data[result_type] = eval_data_handler.get_eval_results(RESULT_PATHS[self.name.lower() + "_all"][result_type])
        
        # convert metrics into a dict
        all_metrics = {}
        for key in all_data:
            all_metrics[key] = all_data[key].get('metrics', {})
            all_metrics[key]["average_answer_length"], all_data[key]['metrics']['average_latency'] = calc_response_level_metrics(all_data[key])
        # convert results into a dataframe
        all_results = {}
        for key in all_data:
            all_results[key] = {}
            all_results[key]['rows'] = pd.DataFrame(all_data[key]['rows'])
            # rename flattened keys to clean column names
            all_results[key]['rows'] = all_results[key]['rows'].rename(columns={
                'inputs.query': 'query',
                'inputs.context': 'context',
                'inputs.response': 'response',
                'inputs.ground_truth': 'ground_truth',
                'inputs.answer_length': 'answer_length',
                'inputs.latency': 'latency',
                'outputs.intend_resolution.intent_resolution': 'intent_resolution',
                'outputs.intend_resolution.intent_resolution_threshold': 'intent_resolution_threshold',
                #'outputs.tool_call_accuracy.tool_call_accuracy': 'tool_call_accuracy',
                #'outputs.tool_call_accuracy.tool_call_accuracy_threshold': 'tool_call_accuracy_threshold',
                'outputs.task_adherence.task_adherence': 'task_adherence',
                'outputs.task_adherence.task_adherence_threshold': 'task_adherence_threshold',
                'outputs.relevance.relevance': 'relevance',
                'outputs.relevance.gpt_relevance': 'gpt_relevance',
                'outputs.relevance.relevance_threshold': 'relevance_threshold',
                'outputs.coherence.coherence': 'coherence',
                'outputs.coherence.gpt_coherence': 'gpt_coherence',
                'outputs.coherence.coherence_threshold': 'coherence_threshold',
                'outputs.fluency.fluency': 'fluency',
                'outputs.fluency.gpt_fluency': 'gpt_fluency',
                'outputs.fluency.fluency_threshold': 'fluency_threshold'
            })
        self.all_results = all_results
        self.all_metrics = all_metrics

        # readteaming
        readteaming_data = eval_data_handler.get_eval_results(RESULT_PATHS[self.name.lower() + "_all"]["redteam"] + "evaluation_results.json")
        """
              "risk_category_summary": [
        {
          "overall_asr": 0.00,
          "hate_unfairness_asr": 0.00,
          "violence_asr": 0.00,
          "sexual_asr": 0.00,
          "self_harm_asr": 0.00
        }
      ],
      "attack_technique_summary":[
        {
          "baseline_asr": 0.00,
          "easy_complexity_asr": 0.00,
          "moderate_complexity_asr": 0.00,
          "difficult_complexity_asr": 0.00
        }
      ],
        """
        self.rt_risk_category_results = pd.DataFrame(readteaming_data['scorecard']['risk_category_summary'])
        self.rt_attack_technique_results = pd.DataFrame(readteaming_data['scorecard']['attack_technique_summary'])


    def end_to_end_model_comparison_table(self) -> None:
        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        model_scores = {}
        for model_type in model_types:
            intent_resolution_score = self.all_metrics[model_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[model_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[model_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[model_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[model_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[model_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[model_type].get('average_answer_length', 0)
            response_time = self.all_metrics[model_type].get('average_latency', 0)
            model_scores[model_type] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for model-based performance
        model_performance_df = pd.DataFrame({ # limit values to 2 decimal places
            'Model': model_types,
            'Intent Resolution': [round(model_scores[model]['Intent Resolution'], 2) for model in model_types],
            #'Tool Call Accuracy': [round(model_scores[model]['Tool Call Accuracy'], 2) for model in model_types],
            'Task Adherence': [round(model_scores[model]['Task Adherence'], 2) for model in model_types],
            'Relevance': [round(model_scores[model]['Relevance'], 2) for model in model_types],
            'Coherence': [round(model_scores[model]['Coherence'], 2) for model in model_types],
            'Fluency': [round(model_scores[model]['Fluency'], 2) for model in model_types],
            'Length (w)': [round(model_scores[model]['Length (w)'], 2) for model in model_types],
            'Time (s)': [round(model_scores[model]['Time (s)'], 2) for model in model_types]
        })
        print(f"End-to-End Model-Based Performance Data:"
                f"\n{model_performance_df.to_string(index=False)}")

    def end_to_end_routing_ablations_comparison_table(self) -> None:
        """
        Compare the performance of different ablations for the end-to-end system.
        """
        ablation_types = ["no_clu", "no_triage", "no_cqa", "no_rag"]
        ablation_scores = {}
        for ablation_type in ablation_types:
            intent_resolution_score = self.all_metrics[ablation_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[ablation_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[ablation_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[ablation_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[ablation_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[ablation_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[ablation_type].get('average_answer_length', 0)
            response_time = self.all_metrics[ablation_type].get('average_latency', 0)
            ablation_scores[ablation_type] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for ablation performance
        ablation_performance_df = pd.DataFrame({
            'Ablation': ['No CLU', 'No Triage', 'No CQA', 'No RAG'],
            'Intent Resolution': [round(ablation_scores[ablate]['Intent Resolution'], 2) for ablate in ablation_types],
            #'Tool Call Accuracy': [round(ablation_scores[ablate]['Tool Call Accuracy'], 2) for ablate in ablation_types],
            'Task Adherence': [round(ablation_scores[ablate]['Task Adherence'], 2) for ablate in ablation_types],
            'Relevance': [round(ablation_scores[ablate]['Relevance'], 2) for ablate in ablation_types],
            'Coherence': [round(ablation_scores[ablate]['Coherence'], 2) for ablate in ablation_types],
            'Fluency': [round(ablation_scores[ablate]['Fluency'], 2) for ablate in ablation_types],
            'Length (w)': [round(ablation_scores[ablate]['Length (w)'], 2) for ablate in ablation_types],
            'Time (s)': [round(ablation_scores[ablate]['Time (s)'], 2) for ablate in ablation_types]
        })
        print(f"End-to-End Ablation Performance Data:"
                f"\n{ablation_performance_df.to_string(index=False)}")
    
    def end_to_end_routing_ablations_aggregate_table(self) -> None:
        """
        Same as the standard routing ablations comparison table.
        But the agentic metrics (intent resolution, task adherence, relevance, coherence, fluency) are aggregated into one score.
        """

        ablation_types = ["gpt4o", "no_clu", "no_triage", "no_cqa", "no_rag"]
        ablation_scores = {}
        for ablation_type in ablation_types:
            intent_resolution_score = self.all_metrics[ablation_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[ablation_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[ablation_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[ablation_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[ablation_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[ablation_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[ablation_type].get('average_answer_length', 0)
            response_time = self.all_metrics[ablation_type].get('average_latency', 0)
            aggregated_score = (intent_resolution_score +
                                task_adherence_score +
                                relevance_score +
                                coherence_score +
                                fluency_score) / 5
            ablation_scores[ablation_type] = {
                'Aggregated Score': aggregated_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for ablation performance
        ablation_performance_df = pd.DataFrame({
            'Ablation': ['None', 'No CLU', 'No Triage', 'No CQA', 'No RAG'],
            'Aggregated Score': [round(ablation_scores[ablate]['Aggregated Score'], 2) for ablate in ablation_types],
            'Length (w)': [round(ablation_scores[ablate]['Length (w)'], 2) for ablate in ablation_types],
            'Time (s)': [round(ablation_scores[ablate]['Time (s)'], 2) for ablate in ablation_types]
        })
        print(f"End-to-End Ablation Aggregate Performance Data:"
                f"\n{ablation_performance_df.to_string(index=False)}")
    
    def end_to_end_aggregate_ablations_box_plot(self) -> None:
        """
        Box plots showing variability in response length across all queries, grouped by ablation type.
        """

        ablation_types = ["gpt4o", "no_clu", "no_triage", "no_cqa", "no_rag"]
        all_ablation_data = {}
        for ablation_type in ablation_types:
            df = self.all_results[ablation_type]['rows']
            # remove extreme outliers (response length > 500 words)
            df = df[df["answer_length"] <= 500]
            all_ablation_data[ablation_type] = df

        # created grouped box plots for response length for each ablation
        sns.boxplot(x="Ablation", y="answer_length",
                data=pd.concat([all_ablation_data[ablate].assign(Ablation=ablate) for ablate in ablation_types]),
                palette="Set2")
        plt.title('Response Length Distribution by Ablation Type')
        plt.xlabel('Ablation Type')
        plt.ylabel('Response Length (words)')
        plt.xticks(ticks=range(len(ablation_types)), labels=['None', 'No CLU', 'No Triage', 'No CQA', 'No RAG'])
        plt.tight_layout()
        plt.savefig(f"{self.figure_filename_st}_aggregate_ablations_box_plot_response_length.png")

    def end_to_end_query_type_comparison_table(self) -> None:
        """
        Compare the performance of different query types for the end-to-end system.
        1. Single-Utterance Queries
        2. Multi-Utterance Queries
        """
        query_types = ["single_utterance_queries", "multi_utterance_queries"]
        query_type_scores = {}
        for query_type in query_types:
            intent_resolution_score = self.all_metrics[query_type].get('intend_resolution.intent_resolution', 0)
            #tool_call_accuracy_score = self.all_metrics[query_type].get('tool_call_accuracy.tool_call_accuracy', 0)
            task_adherence_score = self.all_metrics[query_type].get('task_adherence.task_adherence', 0)
            relevance_score = self.all_metrics[query_type].get('relevance.relevance', 0)
            coherence_score = self.all_metrics[query_type].get('coherence.coherence', 0)
            fluency_score = self.all_metrics[query_type].get('fluency.fluency', 0)
            response_length = self.all_metrics[query_type].get('average_answer_length', 0)
            response_time = self.all_metrics[query_type].get('average_latency', 0)
            query_type_scores[query_type] = {
                'Intent Resolution': intent_resolution_score,
                #'Tool Call Accuracy': tool_call_accuracy_score,
                'Task Adherence': task_adherence_score,
                'Relevance': relevance_score,
                'Coherence': coherence_score,
                'Fluency': fluency_score,
                'Length (w)': response_length,
                'Time (s)': response_time
            }
        # Create a DataFrame for query type performance
        query_type_performance_df = pd.DataFrame({
            'Query Type': ['Single-Utterance', 'Multi-Utterance'],
            'Intent Resolution': [round(query_type_scores[qtype]['Intent Resolution'], 2) for qtype in query_types],
            #'Tool Call Accuracy': [round(query_type_scores[qtype]['Tool Call Accuracy'], 2) for qtype in query_types],
            'Task Adherence': [round(query_type_scores[qtype]['Task Adherence'], 2) for qtype in query_types],
            'Relevance': [round(query_type_scores[qtype]['Relevance'], 2) for qtype in query_types],
            'Coherence': [round(query_type_scores[qtype]['Coherence'], 2) for qtype in query_types],
            'Fluency': [round(query_type_scores[qtype]['Fluency'], 2) for qtype in query_types],
            'Length (w)': [round(query_type_scores[qtype]['Length (w)'], 2) for qtype in query_types],
            'Time (s)': [round(query_type_scores[qtype]['Time (s)'], 2) for qtype in query_types]
        })
        print(f"End-to-End Query Type Performance Data:"
                f"\n{query_type_performance_df.to_string(index=False)}")

    def end_to_end_readteaming_table(self) -> None:
        """
        Table1. summary on risk category results
        Table2. summary on attack technique results
        """
        risk_category_cols_rename = {
            'overall_asr': 'Overall ASR',
            'hate_unfairness_asr': 'Hate/Unfairness ASR',
            'violence_asr': 'Violence ASR',
            'sexual_asr': 'Sexual ASR',
            'self_harm_asr': 'Self-Harm ASR'
        }
        rt_risk_category_results = self.rt_risk_category_results.rename(columns=risk_category_cols_rename)
        rt_risk_category_results = rt_risk_category_results[list(risk_category_cols_rename.values())]
        print("End-to-End Readteaming Risk Category Results:"
              f"\n{rt_risk_category_results.to_string(index=False)}")
        
        attack_technique_cols_rename = {
            'baseline_asr': 'Baseline ASR',
            'easy_complexity_asr': 'Easy Complexity ASR',
            'moderate_complexity_asr': 'Moderate Complexity ASR',
            'difficult_complexity_asr': 'Difficult Complexity ASR'
        }
        rt_attack_technique_results = self.rt_attack_technique_results.rename(columns=attack_technique_cols_rename)
        rt_attack_technique_results = rt_attack_technique_results[list(attack_technique_cols_rename.values())]
        print("End-to-End Readteaming Attack Technique Results:"
              f"\n{rt_attack_technique_results.to_string(index=False)}")

    def end_to_end_model_spider_chart(self) -> None:
        """
        Spider Chart for model-based performance breakdown in the End-to-End system.
        Across 5 metrics: intent resolution, task adherence, relevance, coherence, fluency.
        Scores are between 0 to 5.
        """
        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        metrics = ['intend_resolution.intent_resolution', 'task_adherence.task_adherence', 'relevance.relevance', 'coherence.coherence', 'fluency.fluency']
        metric_labels = ['Intent Resolution', 'Task Adherence', 'Relevance', 'Coherence', 'Fluency']
        num_metrics = len(metrics)

        # Prepare data for spider chart
        angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
        angles += angles[:1]
        plt.figure(figsize=(8, 8))
        for model_type in model_types:
            scores = [self.all_metrics[model_type].get(metric, 0) for metric in metrics]
            scores += scores[:1]
            plt.polar(angles, scores, label=model_type)
        plt.xticks(angles[:-1], metric_labels, size=16)
        plt.yticks([1, 2, 3, 4, 5], color="grey", size=12)
        plt.ylim(0, 5)
        #plt.title('Model-Based Performance (End-To-End System)', size=20, y=1.05)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.figure_filename_st}_spider_chart_model_performance.png")
        
    def end_to_end_query_type_forest_plot(self) -> None:
        """
        Forest Plot. Difference between single-utterance and multi-utterance query performances for each entity (EndToEnd, CampusInfo, AdminInfo, Feedback, ChartPlotter).
        Performance metric: Aggregate Score (mean of intent resolution, task adherence, relevance, coherence, fluency).
        Use case: Visualize effect size and confidence intervals across multiple groups.

        Steps:
        1. For each entity compute mean score for Single-Utterance and Multi-Utterance queries.
        2. The difference is calculated as (Multi-Utterance - Single-Utterance).
        3. Compute 95% confidence intervals for the differences (bootstrap or t-interval).
        4. Plot horizontally: y-axis = entities; x-axis = difference (Δ).
            - Draw a vertical zero line.
            - Each entity is a point at Δ with a whisker for the CI.
            - Highlight the End-to-End row in a distinct color; keep agents in neutral gray.
            - Optionally annotate Δ values at the right.
        """
        
        modular_entities = ["CampusInfo", "AdminInfo", "Feedback", "ChartPlotter"]
        all_entities = ["EndToEnd"] + modular_entities
        entity_scores = {}
        for entity in all_entities:
            if entity == "EndToEnd":
                entity_vis = self
            else:
                entity_vis = AgentVis(agent_name=entity)
            single_utt_intent_resolution = entity_vis.all_metrics["single_utterance_queries"].get('intend_resolution.intent_resolution', 0)
            single_utt_task_adherence = entity_vis.all_metrics["single_utterance_queries"].get('task_adherence.task_adherence', 0)
            single_utt_relevance = entity_vis.all_metrics["single_utterance_queries"].get('relevance.relevance', 0)
            single_utt_coherence = entity_vis.all_metrics["single_utterance_queries"].get('coherence.coherence', 0)
            single_utt_fluency = entity_vis.all_metrics["single_utterance_queries"].get('fluency.fluency', 0)
            single_utt_score = (single_utt_intent_resolution +
                                single_utt_task_adherence +
                                single_utt_relevance +
                                single_utt_coherence +
                                single_utt_fluency) / 5
            multi_utt_intent_resolution = entity_vis.all_metrics["multi_utterance_queries"].get('intend_resolution.intent_resolution', 0)
            multi_utt_task_adherence = entity_vis.all_metrics["multi_utterance_queries"].get('task_adherence.task_adherence', 0)
            multi_utt_relevance = entity_vis.all_metrics["multi_utterance_queries"].get('relevance.relevance', 0)
            multi_utt_coherence = entity_vis.all_metrics["multi_utterance_queries"].get('coherence.coherence', 0)
            multi_utt_fluency = entity_vis.all_metrics["multi_utterance_queries"].get('fluency.fluency', 0)
            multi_utt_score = (multi_utt_intent_resolution +
                                multi_utt_task_adherence +
                                multi_utt_relevance +
                                multi_utt_coherence +
                                multi_utt_fluency) / 5
            score_diff = single_utt_score - multi_utt_score
            # placeholder for confidence intervals
            ci_lower, ci_upper = score_diff - 0.1, score_diff + 0.1
            entity_scores[entity] = {
                'Single-Utterance Score': single_utt_score,
                'Multi-Utterance Score': multi_utt_score,
                'Score Difference': score_diff,
                'CI Lower': ci_lower,
                'CI Upper': ci_upper
            }
        # create a DataFrame for forest plot
        forest_data = []
        for entity, scores in entity_scores.items():
            forest_data.append({
                'Entity': entity,
                'Score Difference': scores['Score Difference'],
                'CI Lower': scores['CI Lower'],
                'CI Upper': scores['CI Upper']
            })
        forest_df = pd.DataFrame(forest_data)
        print(forest_df)

        # plot forest plot
        plt.figure(figsize=(8, 6))
        for i, row in forest_df.iterrows():
            color = 'red' if row['Entity'] == 'EndToEnd' else 'gray'
            plt.plot([row['CI Lower'], row['CI Upper']], [i, i], color=color, marker='o')
            plt.text(row['CI Upper'] + 0.01, i, f"{row['Score Difference']:.2f}", va='center', fontsize=10)
        plt.yticks(range(len(forest_df)), forest_df['Entity'])
        plt.axvline(0, color='black', linestyle='--')
        #plt.title('Forest Plot of Score Differences (Multi-Utterance - Single-Utterance)')
        plt.xlabel('Score Difference (Δ)')
        plt.ylabel('Entity')
        plt.tight_layout()
        plt.savefig(f"{self.figure_filename_st}_forest_plot_query_type_difference.png")
        
    def end_to_end_respones_time_variation_ridgeline(self) -> None:
        """
        ridgline plot that shows repsonse time variation (across all queries) for each model.
        The ridge of each model is on a seperate horizontal level.
        1. Each ridge represents a model: gpt4o, gpt4o_mini, llama3-instruct, phi4_mini_instruct.
        2. The x-axis shows response time (in seconds).
        3. The y-axis stacks the ridges for each model vertically.
        4. The height of each ridge at a given x-value indicates the density of responses with that response time.
        Use case: Compare response time distributions across models in one view.
        """

        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        all_model_data = {}
        for model_type in model_types:
            df = self.all_results[model_type]['rows']
            #df = df[df["latency"] <= 60]  # remove extreme outliers
            all_model_data[model_type] = df

        plt.figure(figsize=(10, 6))
        colors = sns.color_palette("Set2", len(model_types))

        # find global min/max latency for common x grid
        all_latencies = np.concatenate([all_model_data[m]["latency"] for m in model_types])
        x_grid = np.linspace(all_latencies.min(), all_latencies.max(), 500)

        for i, model_type in enumerate(model_types):
            data = all_model_data[model_type]["latency"]
            kde = gaussian_kde(data, bw_method=0.5)
            density = kde(x_grid)
            # normalize density so ridges have consistent heights
            density = density / density.max()

            # offset vertically
            plt.fill_between(x_grid, i, density + i, color=colors[i], alpha=0.6)
            plt.plot(x_grid, density + i, color=colors[i])
            plt.text(all_latencies.min() - 1, i + 0.2, model_type, ha='right', va='center')

        plt.yticks([])
        plt.xlabel('Response Time (s)')
        plt.title('Response Time Variation by Model (Ridgeline Plot)')
        plt.xlim(left=0)
        plt.tight_layout()
        plt.savefig(f"{self.figure_filename_st}_ridgeline_response_time_variation.png")

    def end_to_end_response_time_scatter_animation(self) -> None:
        # --- Collect your data ---
        model_types = ['gpt4o', 'gpt4o_mini', 'llama3-instruct', 'phi4_mini_instruct']
        all_model_data = {}
        for model_type in model_types:
            df = self.all_results[model_type]['rows']
            #df = df[df["latency"] <= 60]  # remove extreme outliers
            all_model_data[model_type] = df["latency"].values

        # --- Prepare scatter points ---
        x_positions = np.arange(len(model_types))  # X positions for each model
        colors = sns.color_palette("Set2", len(model_types))

        # We'll store all scatter points as one list
        scatter_points = []
        fig, ax = plt.subplots(figsize=(8, 6))

        # initial scatter plot
        for i, model_type in enumerate(model_types):
            y_values = all_model_data[model_type]
            # random jitter in x so dots are not on top of each other
            x_jitter = np.random.normal(loc=x_positions[i], scale=0.05, size=len(y_values))
            sc = ax.scatter(x_jitter, y_values, alpha=0.6, color=colors[i], label=model_type)
            scatter_points.append(sc)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(model_types)
        ax.set_ylabel('Response Time (s)')
        ax.set_title('Animated Response Time Variability (Dots Jittering)')
        ax.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # --- Animation update function ---
        def update(frame):
            """Frame update: add jitter to simulate non-determinism"""
            for i, model_type in enumerate(model_types):
                y_values = all_model_data[model_type]
                # apply small random jitter in y for animation effect
                jitter_y = y_values + np.random.normal(0, 0.2, size=len(y_values))  # adjust 0.2 to change wiggle size
                x_jitter = np.random.normal(loc=x_positions[i], scale=0.05, size=len(y_values))
                scatter_points[i].set_offsets(np.column_stack((x_jitter, jitter_y)))
            return scatter_points

        # --- Create animation ---
        anim = FuncAnimation(fig, update, frames=30, interval=300, blit=False, repeat=True)

        # --- Save animation as GIF ---
        gif_filename = f"{self.figure_filename_st}_response_time_jitter.gif"
        anim.save(gif_filename, writer=PillowWriter(fps=5))

        plt.close(fig)  # close the figure so it doesn't display immediately
        print(f"Animation saved as {gif_filename}")


if __name__ == "__main__":
    # 1. CLU results
    #clu_vis = CLUVis()
    #clu_vis.clu_intend_coverage()
    #clu_vis.clu_total_passrate_comparison_table()
    #clu_vis.clu_performance_breakdown_table()
    #clu_vis.clu_performance_breakdown()
    #clu_vis.clu_aggregate_comparison()

    # # 2. CQA results
    # cqa_vis = CQAVis()
    # cqa_vis.cqa_performance_breakdown()

    # # 3. RAG results
    #rag_vis = RAGVis()
    # rag_vis.rag_model_comparison_table()
    # rag_vis.rag_chunk_comparison_table()
    # rag_vis.rag_top_n_comparison_table()
    # rag_vis.rag_performance_breakdown()
    # rag_vis.rag_combined_performance_breakdown()
    #rag_vis.rag_model_bubble_plot()
    #rag_vis.rag_chunk_radar()
    #rag_vis.rag_scatter_top_n()

    # # 4. Agent results
    # agent_vis = AgentVis(agent_name="CampusInfo")
    # #agent_vis.agent_performance_breakdown()
    # agent_vis.agent_model_comparison_table()
    # agent_vis.agent_prompting_strategy_comparison_table()
    # agent_vis.agent_query_type_comparison_table()

    # 5. Combined Agent results
    combined_agent_vis = CombinedAgentVis(agent_names=["CampusInfo", "AdminInfo", "Feedback", "ChartPlotter"])
    #combined_agent_vis.combined_aggregated_performance()
    #combined_agent_vis.combined_grouped_box_plots()
    #combined_agent_vis.combined_prompting_diverging_bar_chart()
    combined_agent_vis.combined_prompting_diverging_bar_chart_horizontal()

    # 5. End-to-End results
    #end_to_end_vis = EndToEndVis()
    #end_to_end_vis.end_to_end_model_comparison_table()
    # end_to_end_vis.end_to_end_routing_ablations_comparison_table()
    #end_to_end_vis.end_to_end_routing_ablations_aggregate_table()
    # end_to_end_vis.end_to_end_query_type_comparison_table()
    # end_to_end_vis.end_to_end_readteaming_table()
    #end_to_end_vis.end_to_end_model_spider_chart()
    #end_to_end_vis.end_to_end_query_type_forest_plot()
    #end_to_end_vis.end_to_end_aggregate_ablations_box_plot()
    #end_to_end_vis.end_to_end_respones_time_variation_ridgeline()
    #end_to_end_response_time_scatter_animation(end_to_end_vis)