/*
 Copyright 2016 SANBI, University of the Western Cape

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var GseaBox = React.createClass({
    getInitialState: function () {
        return {results: [], hash: '', gene_names: []};
    },
    loadResultsFromServer: function () {
        if (this.state.hash != '') {
            $.ajax({
                url: this.props.url + '/' + this.state.hash,
                dataType: 'json',
                cache: false,
                success: function (results) {
                    this.setState({results: results});
                }.bind(this),
                error: function (xhr, status, err) {
                    console.error(this.props.url, status, err.toString());
                }.bind(this)
            })
        }
    },
    componentDidMount: function () {
        this.loadResultsFromServer();
        setInterval(this.loadResultsFromServer, this.props.pollInterval);
    },
    handleGenesetSubmit: function (geneset, mode, multi_comp) {
        var data_string = JSON.stringify({
            geneset: geneset,
            mode: mode,
            multipletest_comp: multi_comp
        });
        // compute hash of the results of this analysis, for caching
        var hash = forge_sha256(data_string);
        this.setState({hash: hash});
        var url_with_hash = this.props.url + '/' + hash
        $.ajax({
            url: url_with_hash,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            type: 'POST',
            data: data_string,
            success: function (results) {
                this.setState({results: results, hash: hash});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url_with_hash, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className="GseaBox">
                <h2 className="center-align light-blue-text text-darken-4">Gene Set Enrichment Analysis (GSEA)</h2>
                <GseaResultList results={this.state.results} hash={this.state.hash}/>
                <GseaForm onGenesetSubmit={this.handleGenesetSubmit} gene_names={this.state.gene_names}/>
            </div>
        );
    }
});

var GseaGalaxyForm = React.createClass({
    getInitialState: function () {
        return ({histories: [], datasets: [], history_id: '', something: ''});
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
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    loadDatasetList: function (history_id) {
        var url = '/api/galaxy_datasets/' + history_id;
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
                this.setState({datasets: dataset_list});
                $('select').material_select();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleHistoryChange: function (e) {
        this.setState({history_id: e.target.value});
    },
    handleDatasetChange: function (e) {

    },
    handleHistoryQueryClick: function () {
        this.loadHistories();
    },
    handleDatasetQueryClick: function () {
        this.loadDatasetList(this.state.history_id);
    },
    populateQueryForm: function () {

    },
    componentDidMount: function () {
        $(document).ready(function () {
            $('history_select').material_select();
        });
    },
    render: function () {
        var history_options = this.state.histories.map(function (history) {
            return (
                <option key={history.id} value={history.id}>{history.name}</option>
            )
        });
        var dataset_options = this.state.datasets.map(function (dataset) {
            return (
                <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
            )
        });
        var history_select;
        var dataset_query;
        if (this.state.histories.length > 0) {
            history_select =
                <div className="input-field col-3">
                    <select id="history_select" value={this.state.history_id} onChange={this.handleHistoryChange}>
                        { history_options }
                    </select>
                </div>;
            dataset_query =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.handleDatasetQueryClick}>Query Galaxy Datasets
                    </button>
                </div>;
        }
        var dataset_select;
        var dataset_populate;
        if (this.state.datasets.length > 0) {
            dataset_select =
                <div className="input-field col-3">
                    <select id="dataset_set" value={this.state.dataset_id} onChange={this.handleDatasetChange}>
                        { dataset_options }
                    </select>
                </div>;
            dataset_populate =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onclick={this.populateQueryForm}>Load Dataset to Query
                    </button>
                </div>
        }
        return (
            <div className="row">
                <div classname="col s12">
                    <div className="input-field col-6">
                        <button className="btn waves-effect waves-light light-blue darken-4"
                                onClick={this.handleHistoryQueryClick}>Query Galaxy Histories
                        </button>
                        { dataset_query }
                        { dataset_populate }
                    </div>
                    { history_select }
                    { dataset_select }
                </div>
            </div>
        )
    }
});

var GseaForm = React.createClass({
    getInitialState: function () {
        return {
            text: '', mode: 'over', multi_comp: 'fdr_bh',
            histories: [], datasets: [],
            history_id: '', dataset_id: ''
        };
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
    loadDatasetList: function (history_id) {
        var url = '/api/galaxy_datasets/' + history_id;
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
    loadGeneNames: function (dataset_id) {
        var url = '/api/galaxy_dataset/' + dataset_id;
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                var newtext = data.trim().split('\n').map(function (line) {
                    return line.trim().split(/\s+/)[0].replace("rv_", "Rv");
                }).join('\n');
                this.setState({text: newtext});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(status, err.toString());
            }.bind(this)
        });
    },
    handleHistoryChange: function (e) {
        this.setState({history_id: e.target.value});
    },
    handleDatasetChange: function (e) {
        this.setState({dataset_id: e.target.value});
    },
    handleHistoryQueryClick: function () {
        this.loadHistories();
    },
    handleDatasetQueryClick: function () {
        this.loadDatasetList(this.state.history_id);
    },
    populateQueryForm: function () {
        this.loadGeneNames(this.state.dataset_id);
    },
    handleTextChange: function (e) {
        this.setState({text: e.target.value});
    },
    handleModeChange: function (e) {
        this.setState({mode: e.target.value});
    },
    handleMultiCompChange: function (e) {
        this.setState({multi_comp: e.target.value});
    },
    handleSubmit: function (e) {
        e.preventDefault();
        var geneset_str = this.state.text.trim();
        if (!geneset_str)
            return;
        var geneset = geneset_str.split(/\n|\r/);
        geneset = geneset.map(function (gene_name) {
            return (gene_name.replace('rv_', 'Rv'));
        });
        this.props.onGenesetSubmit(geneset, this.state.mode, this.state.multi_comp);
        this.setState({text: ''});
    },
    componentDidMount: function () {
        $(document).ready(function () {
            $("select").material_select();
        });
        $('#modeselectdiv').on('change', 'select', null, this.handleModeChange);
        $('#multicompselectdiv').on('change', 'select', null, this.handleMultiCompChange);

    },
    render: function () {
        var history_options = this.state.histories.map(function (history) {
            return (
                <option key={history.id} value={history.id}>{history.name}</option>
            )
        });
        var dataset_options = this.state.datasets.map(function (dataset) {
            return (
                <option key={dataset.id} value={dataset.id}>{dataset.name}</option>
            )
        });
        var history_select;
        var dataset_query;
        if (this.state.histories.length > 0) {
            history_select =
                <div id="historyselectdiv" className="input-field col-3">
                    <select id="historyselect" value={this.state.history_id}>
                        { history_options }
                    </select>
                </div>;
            dataset_query =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.handleDatasetQueryClick}>Query Galaxy Datasets
                    </button>
                </div>;
        }
        var dataset_select;
        var dataset_populate;
        if (this.state.datasets.length > 0) {
            dataset_select =
                <div id="datasetselectdiv" className="input-field col-3">
                    <select id="datasetselect" value={this.state.dataset_id} onChange={this.handleDatasetChange}>
                        { dataset_options }
                    </select>
                </div>;
            dataset_populate =
                <div className="input-field col-3">
                    <button className="btn waves-effect waves-light light-blue darken-4"
                            onClick={this.populateQueryForm}>Load Dataset to Query
                    </button>
                </div>
        }

        return (
            <div className="row">
                <div classname="col s12">
                    <div className="input-field col-6">
                        <button className="btn waves-effect waves-light light-blue darken-4"
                                onClick={this.handleHistoryQueryClick}>Query Galaxy Histories
                        </button>
                        { dataset_query }
                    </div>
                    { history_select }
                    { dataset_select }
                    { dataset_populate }
                </div>
                <form className="col s12" onSubmit={this.handleSubmit}>
                    <div className="input-field col s12">
                        <textarea className="materialize-textarea"
                                  placeholder="A list of locus tags"
                                  value={this.state.text}
                                  onChange={this.handleTextChange}>
                        </textarea>
                    </div>
                    <div id="modeselectdiv" className="input-field col s6">
                        <select value={this.state.mode} onChange={this.handleModeChange}>
                            <option value="over">Test for overrepresentation</option>
                            <option value="under">Test for underrepresentation</option>
                        </select>
                        <label>Test type</label>
                    </div>
                    <div id="multicompselectdiv" className="input-field col s6">
                        <select value={this.state.multi_comp} onChange={this.handleMultiCompChange}>
                            <option value="fdr_bh">Benjamini-Hochberg</option>
                            <option value="bonferroni">Bonferroni</option>
                        </select>
                        <label>Multiple testing correction type</label>
                    </div>
                    <div className="input-field col s6">
                        <button className="btn waves-effect waves-light light-blue darken-4"
                                type="submit"
                        >Submit
                        </button>
                    </div>
                </form>
            </div>
        );
    }
});

var GseaResultList = React.createClass({
    makedownload: function () {

    },
    render: function () {
        if (this.props.results.length == 0)
            return (<span>Paste a list of locus tags (RvXXXX) in the box below and click the Submit button.</span>);
        else {
            var resultLines = this.props.results.map(function (row, i) {
                return (
                    <tr key={i}>
                        {row.map(function (col, j) {
                            return <td key={j}>{col}</td>
                        })}
                    </tr>
                );
            });
            var downloadLink = '/api/gsea/' + this.props.hash + '/download';
            return (
                <div className="col s12">
                    <a className="waves-effect waves-light btn light-blue darken-4" href={downloadLink}>Download</a>
                    <table className="striped">
                        <thead>
                        <tr>
                            <th data-field="goterm">GO Term ID</th>
                            <th>GO Term Name</th>
                            <th>Raw p-value</th>
                            <th>Corrected p-value</th>
                        </tr>
                        </thead>
                        <tbody>
                        {resultLines}
                        </tbody>
                    </table>
                </div>
            );
        }
    }
});

ReactDOM.render(
    <GseaBox url="/api/gsea" pollInterval={2000}/>,
    document.getElementById('gsea_container')
);