(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * Created by thoba on 2017/02/02.
 */

var VcfContainer = React.createClass({displayName: "VcfContainer",
    getInitialState: function () {
        return {
            firstName: '', lastName: '',
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [],
            history_id: '', dataset_id: ''
        };
    },
    componentWillMount: function () {
        console.log('ComponentWillMount')
    },
    componentDidMount: function () {
        console.log('ComponentDidMount');
        $(document).ready(function () {
            $('select').material_select();
        });
        this.loadHistories();
    },
    componentWillUnmount: function () {
        console.log('ComponentWillUnmout')
    },
    loadHistories: function () {
        $.ajax({
            url: '/api/galaxy_histories',
            dataType: 'json',
            cache: false,
            success: function (histories) {
                var history_list = [];
                var history_length = histories.length;
                for (var i = 0; i < history_length; i++) {
                    history_list.push({'name': histories[i]['name'], id: histories[i]['id']});
                }
                this.setState({histories: history_list, history_id: history_list[0].id});
                $('select').material_select();
                $('#historyselectdiv').on('change', 'select', null, this.handleHistoryChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleHistoryChange: function (e) {
        this.setState({history_id: e.target.value});
    },
    render: function () {
        console.log('render');
        return (
            React.createElement("div", null, 
                React.createElement("h2", null, 
                    this.props.message
                ), 
                React.createElement(HelloReact, {histories: this.state.histories, history_id: this.state.history_id})
            )

        )
    }
});

var HelloReact = React.createClass({displayName: "HelloReact",
    getInitialState: function () {
        return {
            firstName: '', lastName: '',
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [], dataset_cols: [],
            history_id: '', dataset_id: '', dataset_col_id: ''
        };
    },
    componentWillMount: function () {
        console.log('ComponentWillMount')
    },
    componentDidMount: function () {
        $(document).ready(function () {
            $('select').material_select();
        });
        // this.loadHistories();
        console.log('ComponentDidMount')
    },
    componentWillUnmount: function () {
        console.log('ComponentWillUnmout')
    },
    loadDatasetColList: function (history_id) {
        var url = '/api/galaxy_dataset_col/' + history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                var dataset_list = [];
                var dataset_list_length = datasets.length;
                for (var i = 0; i < dataset_list_length; i++) {
                    dataset_list.push({'name': datasets[i]['name'], id: datasets[i]['id']});
                }
                this.setState({dataset_cols: dataset_list, dataset_col_id: dataset_list[0].id});
                $('select').material_select();
                $('#datasetcolselectdiv').on('change', 'select', null, this.handleDatasetColChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    loadDatasetList: function (history_id) {
        var url = '/api/galaxy_col_datasets/' + history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                var dataset_list = [];
                var dataset_list_length = datasets.length;
                for (var i = 0; i < dataset_list_length; i++) {
                    dataset_list.push({'name': datasets[i]['name'], id: datasets[i]['id']});
                }
                this.setState({datasets: dataset_list, dataset_id: dataset_list[0].id});
                $('select').material_select();
                $('#datasetselectdiv').on('change', 'select', null, this.handleDatasetChange);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleDatasetColQueryClick: function () {
        this.loadDatasetColList(this.props.history_id);
    },
    handleDatasetQueryClick: function () {
        this.loadDatasetList(this.props.history_id);
    },
    handleDatasetColChange: function (e) {
        this.setState({dataset_col_id: e.target.value});
    },
    handleDatasetChange: function (e) {
        this.setState({dataset_id: e.target.value});
    },
    render: function () {
        var history_options = this.props.histories.map(function (history) {
            return (
                React.createElement("option", {key: history.id, value: history.id}, history.name)
            )
        });
        var dataset__col_options = this.state.dataset_cols.map(function (dataset) {
            return (
                React.createElement("option", {key: dataset.id, value: dataset.id}, dataset.name)
            )
        });
        var dataset_options = this.state.datasets.map(function (dataset) {
            return (
                React.createElement("option", {key: dataset.id, value: dataset.id}, dataset.name)
            )
        });
        var history_select;
        var dataset_col_query;
        if (this.props.histories.length > 0) {
            history_select =
                React.createElement("div", {id: "historyselectdiv", className: "input-field col-3"}, 
                    React.createElement("select", {id: "historyselect", value: this.props.history_id}, 
                         history_options 
                    ), 
                    React.createElement("label", null, "Select History")
                );
            dataset_col_query =
                React.createElement("div", {className: "input-field col-3"}, 
                    React.createElement("button", {className: "btn waves-effect waves-light light-blue darken-4", 
                            onClick: this.handleDatasetColQueryClick}, "Get History Datasets Collections"
                    )
                );
        }
        var dataset_col_select;
        var col_dataset_query;
        if (this.state.dataset_cols.length > 0) {
            dataset_col_select =
                React.createElement("div", {id: "datasetcolselectdiv", className: "input-field col-3"}, 
                    React.createElement("select", {id: "datasetcolselect", value: this.state.dataset_col_id}, 
                         dataset__col_options 
                    ), 
                    React.createElement("label", null, "Select Dataset Collection")
                );
            col_dataset_query =
                React.createElement("div", {className: "input-field col-3"}, 
                    React.createElement("button", {className: "btn waves-effect waves-light light-blue darken-4", 
                            onClick: this.handleDatasetQueryClick}, "Get Collection Datasets"
                    )
                );
        }
        var dataset_select;
        if (this.state.datasets.length > 0) {
            dataset_select =
                React.createElement("div", {id: "datasetselectdiv", className: "input-field col-3"}, 
                    React.createElement("select", {multiple: true, id: "datasetselect", value: this.state.dataset_id}, 
                         dataset_options 
                    ), 
                    React.createElement("label", null, "Select Dataset")
                );
        }
        return (
            React.createElement("div", null, 
                React.createElement("h2", {className: "center-align light-blue-text text-darken-4"}, "Import VCF from Galaxy"), 
                React.createElement("div", {className: "row center"}, 
                    React.createElement("h6", {className: "header col s12"}, "Import VCF collections from your Galaxy Histories.")
                ), 
                /*<HelloMessage className="center-align light-blue-text text-darken-4" message=""/>*/
                React.createElement("div", {className: "input-field col s12"}, 
                    history_select, 
                    dataset_col_query, 
                    React.createElement("br", null), 
                     dataset_col_select, 
                    col_dataset_query, 
                    React.createElement("br", null), 
                    dataset_select
                )
            )
        )
    }
});

ReactDOM.render(
    React.createElement(VcfContainer, null)
    , document.getElementById('vcf'));

},{}]},{},[1]);
