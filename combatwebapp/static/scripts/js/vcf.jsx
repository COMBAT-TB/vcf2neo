(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

/**
 * Created by thoba on 2017/02/02.
 */

var VcfContainer = React.createClass({
    displayName: 'VcfContainer',

    getInitialState: function getInitialState() {
        return {
            firstName: '', lastName: '',
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [],
            history_id: '', dataset_id: ''
        };
    },
    componentWillMount: function componentWillMount() {
        console.log('ComponentWillMount');
    },
    componentDidMount: function componentDidMount() {
        console.log('ComponentDidMount');
        $(document).ready(function () {
            $('select').material_select();
        });
        this.loadHistories();
    },
    componentWillUnmount: function componentWillUnmount() {
        console.log('ComponentWillUnmout');
    },
    loadHistories: function loadHistories() {
        $.ajax({
            url: '/api/galaxy_histories',
            dataType: 'json',
            cache: false,
            success: function (histories) {
                var history_list = [];
                var history_length = histories.length;
                for (var i = 0; i < history_length; i++) {
                    history_list.push({ 'name': histories[i]['name'], id: histories[i]['id'] });
                }
                this.setState({ histories: history_list, history_id: history_list[0].id });
                $('select').material_select();
                $('#historyselectdiv').on('change', 'select', null, this.handleHistoryChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleHistoryChange: function handleHistoryChange(e) {
        this.setState({ history_id: e.target.value });
    },
    render: function render() {
        console.log('render');
        return React.createElement(
            'div',
            null,
            React.createElement(
                'h2',
                null,
                this.props.message
            ),
            React.createElement(HelloReact, { histories: this.state.histories, history_id: this.state.history_id })
        );
    }
});

var HelloReact = React.createClass({
    displayName: 'HelloReact',

    getInitialState: function getInitialState() {
        return {
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [], dataset_cols: [],
            history_id: '', dataset_id: '', dataset_col_id: '',
            selected_datasets: [], loaded_datasets: []
        };
    },
    componentWillMount: function componentWillMount() {
        console.log('ComponentWillMount');
    },
    componentDidMount: function componentDidMount() {
        $(document).ready(function () {
            $('select').material_select();
        });
        console.log('ComponentDidMount');
    },
    componentWillUnmount: function componentWillUnmount() {
        console.log('ComponentWillUnmout');
    },
    loadDatasetColList: function loadDatasetColList(history_id) {
        var url = '/api/galaxy_dataset_col/' + history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                var dataset_list = [];
                var dataset_list_length = datasets.length;
                for (var i = 0; i < dataset_list_length; i++) {
                    dataset_list.push({ 'name': datasets[i]['name'], id: datasets[i]['id'] });
                }
                this.setState({ dataset_cols: dataset_list, dataset_col_id: dataset_list[0].id });
                $('select').material_select();
                $('#datasetcolselectdiv').on('change', 'select', null, this.handleDatasetColChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    loadDatasetList: function loadDatasetList(history_id) {
        var url = '/api/galaxy_col_datasets/' + history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                var dataset_list = [];
                var dataset_list_length = datasets.length;
                for (var i = 0; i < dataset_list_length; i++) {
                    dataset_list.push({ 'name': datasets[i]['name'], id: datasets[i]['id'] });
                }
                this.setState({ datasets: dataset_list, dataset_id: dataset_list[0].id });
                $('select').material_select();
                $('#datasetselectdiv').on('change', 'select', null, this.handleDatasetChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleDatasetColQueryClick: function handleDatasetColQueryClick() {
        this.loadDatasetColList(this.props.history_id);
    },
    handleDatasetQueryClick: function handleDatasetQueryClick() {
        this.loadDatasetList(this.props.history_id);
    },
    handleDatasetColChange: function handleDatasetColChange(e) {
        this.setState({ dataset_col_id: e.target.value });
    },
    handleDatasetChange: function handleDatasetChange(e) {
        this.setState({ dataset_id: e.target.value });
    },
    handleDatasetSelectChange: function handleDatasetSelectChange(e) {
        var options = e.target.options;
        var values = [];
        for (var i = 0, l = options.length; i < l; i++) {
            if (options[i].selected) {
                values.push(options[i].value);
            }
        }
        console.log(values);
        this.setState({ selected_datasets: values });
    },
    loadColDataset: function loadColDataset() {
        var url = '/api/load_col_datasets/' + this.props.history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                console.log(datasets);
                this.setState({ loaded_datasets: datasets });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    loadDataset: function loadDataset() {
        var url = '/api/load_galaxy_dataset/' + this.state.selected_datasets;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                console.log(datasets);
                this.setState({ loaded_datasets: datasets });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    render: function render() {
        var history_options = this.props.histories.map(function (history) {
            return React.createElement(
                'option',
                { key: history.id, value: history.id },
                history.name
            );
        });
        var dataset_col_options = this.state.dataset_cols.map(function (dataset) {
            return React.createElement(
                'option',
                { key: dataset.id, value: dataset.id },
                dataset.name
            );
        });
        var dataset_options = this.state.datasets.map(function (dataset) {
            return React.createElement(
                'option',
                { key: dataset.id, value: dataset.id },
                dataset.name
            );
        });
        var history_select;
        var dataset_col_query;
        if (this.props.histories.length > 0) {
            history_select = React.createElement(
                'div',
                { id: 'historyselectdiv', className: 'input-field col-3' },
                React.createElement(
                    'select',
                    { id: 'historyselect', value: this.props.history_id },
                    history_options
                ),
                React.createElement(
                    'label',
                    null,
                    'Select History'
                )
            );
            dataset_col_query = React.createElement(
                'div',
                { className: 'input-field col-3' },
                React.createElement(
                    'button',
                    { className: 'btn waves-effect waves-light light-blue darken-4',
                        onClick: this.handleDatasetColQueryClick },
                    'Get History Datasets Collections'
                )
            );
        }
        var dataset_col_select;
        // var col_dataset_query;
        var load_col_datasets;
        if (this.state.dataset_cols.length > 0) {
            dataset_col_select = React.createElement(
                'div',
                { id: 'datasetcolselectdiv', className: 'input-field col-3' },
                React.createElement(
                    'select',
                    { id: 'datasetcolselect', value: this.state.dataset_col_id },
                    dataset_col_options
                ),
                React.createElement(
                    'label',
                    null,
                    'Select Dataset Collection'
                )
            );
            load_col_datasets = React.createElement(
                'div',
                { className: 'input-field col-3' },
                React.createElement(
                    'button',
                    { className: 'btn waves-effect waves-light light-blue darken-4',
                        onClick: this.loadColDataset },
                    'Load Collection Dataset(s)'
                )
            );
            // col_dataset_query =
            //     <div className="input-field col-3">
            //         <button className="btn waves-effect waves-light light-blue darken-4"
            //                 onClick={this.handleDatasetQueryClick}>Get Collection Datasets
            //         </button>
            //     </div>;
        }
        var dataset_select;
        var load_dataset;
        if (this.state.datasets.length > 0) {
            dataset_select = React.createElement(
                'div',
                { id: 'datasetselectdiv', className: 'input-field col-3' },
                React.createElement(
                    'select',
                    { className: 'browser-default', id: 'datasetselect', onChange: this.handleDatasetSelectChange,
                        multiple: true },
                    dataset_options
                )
            );
            load_dataset = React.createElement(
                'div',
                { className: 'input-field col-3' },
                React.createElement(
                    'button',
                    { className: 'btn waves-effect waves-light light-blue darken-4',
                        onClick: this.loadDataset },
                    'Load Dataset(s)'
                )
            );
        }
        var imported_data;
        if (this.state.loaded_datasets.length > 0) {
            imported_data = React.createElement(
                'div',
                { className: 'row' },
                React.createElement(
                    'div',
                    { className: 'card-panel teal lighten-2 center-align' },
                    'Successfully loaded ',
                    this.state.loaded_datasets.length,
                    ' VCF files.'
                )
            );
        }
        return React.createElement(
            'div',
            null,
            React.createElement(
                'h2',
                { className: 'center-align light-blue-text text-darken-4' },
                'Import VCF from Galaxy'
            ),
            React.createElement(
                'div',
                { className: 'row center' },
                React.createElement(
                    'h6',
                    { className: 'header col s12' },
                    'Import VCF collections from your Galaxy Histories.'
                )
            ),
            React.createElement(
                'div',
                { className: 'input-field col s12' },
                history_select,
                dataset_col_query,
                React.createElement('br', null),
                dataset_col_select,
                load_col_datasets,
                React.createElement('br', null),
                imported_data
            )
        );
    }
});

ReactDOM.render(React.createElement(VcfContainer, null), document.getElementById('vcf'));

},{}]},{},[1]);
