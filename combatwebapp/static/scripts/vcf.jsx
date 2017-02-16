/**
 * Created by thoba on 2017/02/02.
 */

var VcfContainer = React.createClass({
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
            <div>
                <h2>
                    {this.props.message}
                </h2>
                <HelloReact histories={this.state.histories} history_id={this.state.history_id}/>
            </div>

        )
    }
});

var HelloReact = React.createClass({
    getInitialState: function () {
        return {
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [], dataset_cols: [],
            history_id: '', dataset_id: '', dataset_col_id: '',
            selected_datasets: [], loaded_datasets: []
        };
    },
    componentWillMount: function () {
        console.log('ComponentWillMount')
    },
    componentDidMount: function () {
        $(document).ready(function () {
            $('select').material_select();
        });
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
    handleDatasetSelectChange: function (e) {
        var options = e.target.options;
        var values = [];
        for (var i = 0, l = options.length; i < l; i++) {
            if (options[i].selected) {
                values.push(options[i].value);
            }
        }
        console.log(values);
        this.setState({selected_datasets: values});
    },
    loadColDataset: function () {
        var url = '/api/load_col_datasets/' + this.props.history_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                console.log(datasets);
                this.setState({loaded_datasets: datasets});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    loadDataset: function () {
        var url = '/api/load_galaxy_dataset/' + this.state.selected_datasets;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (datasets) {
                console.log(datasets);
                this.setState({loaded_datasets: datasets});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        var history_options = this.props.histories.map(function (history) {
            return (
                <option key={history.id} value={history.id}>{history.name}</option>
            )
        });
        var dataset_col_options = this.state.dataset_cols.map(function (dataset) {
            return (
                <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
            )
        });
        var dataset_options = this.state.datasets.map(function (dataset) {
            return (
                <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
            )
        });
        var history_select;
        var dataset_col_query;
        if (this.props.histories.length > 0) {
            history_select =
                <div id="historyselectdiv" className="input-field col-3">
                    <select id="historyselect" value={this.props.history_id}>
                        { history_options }
                    </select>
                    <label>Select History</label>
                </div>;
            dataset_col_query =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.handleDatasetColQueryClick}>Get History Datasets Collections
                    </button>
                </div>;
        }
        var dataset_col_select;
        // var col_dataset_query;
        var load_col_datasets;
        if (this.state.dataset_cols.length > 0) {
            dataset_col_select =
                <div id="datasetcolselectdiv" className="input-field col-3">
                    <select id="datasetcolselect" value={this.state.dataset_col_id}>
                        { dataset_col_options }
                    </select>
                    <label>Select Dataset Collection</label>
                </div>;
            load_col_datasets =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.loadColDataset}>Load Collection Dataset(s)
                    </button>
                </div>;
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
            dataset_select =
                <div id="datasetselectdiv" className="input-field col-3">
                    <select className="browser-default" id="datasetselect" onChange={this.handleDatasetSelectChange}
                            multiple={true}>
                        { dataset_options }
                    </select>
                    {/*<label>Select Dataset</label>*/}
                </div>;
            load_dataset =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.loadDataset}>Load Dataset(s)
                    </button>
                </div>;
        }
        return (
            <div>
                <h2 className="center-align light-blue-text text-darken-4">Import VCF from Galaxy</h2>
                <div className="row center">
                    <h6 className="header col s12">Import VCF collections from your Galaxy Histories.</h6>
                </div>
                {/*<HelloMessage className="center-align light-blue-text text-darken-4" message=""/>*/}
                <div className="input-field col s12">
                    {history_select}
                    {dataset_col_query}
                    <br/>
                    {dataset_col_select}
                    {load_col_datasets}
                    {/*{col_dataset_query}*/}
                    <br/>
                    {dataset_select}
                    {load_dataset}
                </div>
            </div>
        )
    }
});

ReactDOM.render(
    <VcfContainer />
    , document.getElementById('vcf'));