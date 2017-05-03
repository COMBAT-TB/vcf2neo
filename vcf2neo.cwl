#!/usr/bin/env cwl-runner

$namespaces:
  dct: http://purl.org/dc/terms/
  foaf: http://xmlns.com/foaf/0.1/

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf

class: "CommandLineTool"
id: "vcf2neo"
label: "Import collection of VCF files to Neo4J DB"
cwlVersion: v1.0
doc: |
    ![build_status](https://quay.io/repository/sanbi-sa/vcf2neo/status)
    The vcf2neo tool imports VCF files into a Neo4J database following the
    COMBAT TB (GA4GH based) Variant schema.

dct:creator:
  foaf:name: Thoba Lose
  foaf:mbox: "mailto:thoba@sanbi.ac.za"

requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: DB
        envValue: $(inputs.database_host)
      - envName: NEO4J_PASSWORD
        envValue: $(inputs.database_password)

hints:
  - class: DockerRequirement
    dockerPull: "quay.io/sanbi-sa/vcf2neo:0.0.3"
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 128

inputs:
  database_host:
    label: "IP or hostname of Neo4J database host"
    type: string?
    default: 192.168.2.211
  database_password:
    label: "Neo4J database password"
    type: string?
    default: ""
  no_docker:
    label: "Skip use of Docker container"
    type: boolean?
    inputBinding:
      prefix: -D
      position: 1
  vcf_dir:
    label: "VCF file location"
    type: Directory
    inputBinding:
      position: 2
  owner:
    label: "Username of owner"
    type: string
    inputBinding:
      position: 3
  history_id:
    label: "ID of Galaxy history VCF came from"
    type: string?
    inputBinding:
      position: 4
  refdb_dir:
    label: "Directory containing Neo4J database of reference data"
    type: Directory?
    inputBinding:
      position: 5

stdout: vcf2neo_report.out.txt
stderr: vcf2neo_report.err.txt

outputs:
  output_report:
    type: stdout
  error_report:
    type: stderr

baseCommand: ["vcf2neo", "init"]
