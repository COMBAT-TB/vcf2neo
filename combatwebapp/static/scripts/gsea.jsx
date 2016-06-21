
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
    getInitialState: function() {
        return { results: [], hash: ''};
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
    componentDidMount: function() {
        this.loadResultsFromServer();
        setInterval(this.loadResultsFromServer, this.props.pollInterval);
    },
    handleGenesetSubmit: function(geneset, mode, multi_comp) {
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
            success: function(results) {
                this.setState({ results: results, hash: hash });
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url_with_hash, status, err.toString());
            }.bind(this)
        });
    },
    render: function() {
        return(
          <div className="GseaBox">
            <h2 className="center-align">geneset enrichment analysis</h2>
              <GseaResultList results={this.state.results} hash={this.state.hash} />
              <GseaForm onGenesetSubmit={this.handleGenesetSubmit} />
          </div>
        );
    }
});

var GseaForm = React.createClass({
    getInitialState: function() {
        return {text: '', mode: 'over', multi_comp: 'fdr_bh'};
    },
    handleTextChange: function(e) {
        this.setState({text: e.target.value});
    },
    handleModeChange: function(e) {
        this.setState({mode: e.target.value});
    },
    handleMultiCompChange: function(e) {
        this.setState({multi_comp: e.target.value});
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var geneset_str = this.state.text.trim();
        if (!geneset_str)
            return;
        var geneset = geneset_str.split(/\n|\r/);
        geneset = geneset.map(function(gene_name) {
            return(gene_name.replace('rv_', 'Rv'));
        });
        this.props.onGenesetSubmit(geneset, this.state.mode, this.state.multi_comp);
        this.setState({text: ''});
    },
    componentDidMount: function() {
        $(document).ready(function() {
        $('select').material_select();
        });
    },
    render: function() {

          return(
              <div className="row">
                  <form className="col s12" onSubmit={this.handleSubmit}>
                      <div className="input-field col s12">
                        <textarea className="materialize-textarea"
                            placeholder="A list of locus tags"
                            value={this.state.text}
                            onChange={this.handleTextChange}>
                        </textarea>
                      </div>
                      <div className="input-field col s6">
                          <select value={this.state.mode} onChange={this.handleModeChange}>
                              <option value="over">Test for overrepresentation</option>
                              <option value="under">Test for underrepresentation</option>
                          </select>
                          <label>Test type</label>
                      </div>
                      <div className="input-field col s6">
                          <select value={this.state.multi_comp} onChange={this.handleMultiCompChange}>
                              <option value="fdr_bh">Benjamini-Hochberg</option>
                              <option value="bonferroni">Bonferroni</option>
                          </select>
                          <label>Multiple testing correction type</label>
                      </div>
                      <div className="input-field col s6">
                        <button className="btn waves-effect waves-light"
                          type="submit"
                        >Submit</button>
                       </div>
                  </form>
              </div>
          );
    }
});

var GseaResultList = React.createClass({
    makedownload: function () {

    },
    render: function() {
        if (this.props.results.length == 0)
            return(<span>Paste a list of locus tags (RvXXXX) in the box below and click the Submit button.</span>);
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
                    <a className="waves-effect waves-light btn" href={downloadLink}>Download</a>
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
    <GseaBox url="/api/gsea" pollInterval={2000} />,
    document.getElementById('gsea_container')
);