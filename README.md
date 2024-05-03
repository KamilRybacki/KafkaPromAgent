# Kafka+PrometheusAgent (KPA) stack

Custom Ansible roles for deploying Prometheus in Agent mode that scrapes
metrics from configured targets and sends them to a Kafka topic.
The [Kafka adapter] is used as a remote write endpoint for Prometheus.

These playbooks deploys the following components on default:

* Prometheus Operator and CRDs
* Prometheus in Agent Mode
* Kafka with Prometheus Adapter as remote write endpoint

A `kubeconfig` file is required to run these playbooks on each host
with the `kubectl` priviledges. It must be located under the path
specified in the settings shown below.

## Configuration

The configuration of individual components is done
via Ansible variables.

The default values for each of them are located
in the `roles/<component>/defaults/main.yml` files.

These variables can be overriden by defining them
in the `environments/<env>/group_vars.yml` file
or in the `group_vars` directory, in a file named
after the group name (default is: `kpa`).

### General

These values configure the stack as a whole
and *must* be defined either in the
`environments/<env>/group_vars.yml` file or in
the `group_vars` directory, in a file named
after the group name (default is: `kpa`):

#### Installation settings

* `kpa_target_state` -
Enable KPA components (default: `present`)
* `kpa_stack_values_files_dir` -
Directory for saving automatically generated
values files for the stack
(default: `environments/<env>/values`)
* `kpa_kubeconfig_path` -
Path to the `kubeconfig` file for the host
(default: `$HOME/.kube/config`)

#### Cluster specific settings

* `kpa_namespace` -
Namespace to deploy KPA components to (default: `kpa`)
* `kpa_cluster_domain` -
Cluster domain for KPA components (default: `cluster.local`)

All resources deployed by these playbooks are created
in the `kpa_namespace` by default namespace for
correct resolution of DNS names.

### Kafka configuration

These variables configure the Kafka component:

* `kafka_replicas` -
Number of Kafka replicas (default: `1`)
* `kafka_client_port` -
Port for Kafka client (default: `9092`)
* `kafka_controller_port` -
Port for Kafka controller (default: `9093`)
* `kafka_internal_port` -
Port for Kafka internal communications (default: `9094`)
* `kafka_external_port` -
Port for Kafka external communications (default: `9095`)

* `kafka_cpu_request` -
CPU request for Kafka pods (default: `100m`)
* `kafka_cpu_limit` -
CPU limit for Kafka pods (default: `500m`)
* `kafka_memory_request` -
Memory request for Kafka pods (default: `128Mi`)
* `kafka_memory_limit` -
Memory limit for Kafka pods (default: `2048Mi`)

* `kafka_log_retention_time_in_hours` -
Log retention time in hours for Kafka (default: `168`)
* `kafka_log_retention_bytes` -
Log retention bytes for Kafka (default: `1073741824`)
* `kafka_persistence_size` -
Persistence size for Kafka (default: `8Gi`)
* `kafka_persistence_storage_class` -
Persistence storage class for Kafka (default: `""`)
* `kafka_persistence_access_mode` -
Persistence access mode for Kafka (default: `ReadWriteOnce`)
* `kafka_extra_env_vars_mode` -
One of possible [modes of passing extra environment variables]
for Kafka (default: `list`)
* `kafka_extra_env_vars` -
Extra environment variables for Kafka in the format
corresponding to the chosen mode (default: `[]`)

#### Further Kafka customization

* `kafka_extra_values` -
Additional values for Kafka Helm Chart (default: `{}`)

The additional contents of the values file should be
passed to the `kafka_extra_values` variable in YAML format.

This variable is to be used for customizing other components
deployed via this playbook, which are disabled by default i.e.
the Prometheus Alertmanager, Kube-state-metrics
and Prometheus Node Exporter. Please refer to the
[Values file present in the Kafka Helm chart repository]
to check all available options for them (and for their defaults).

Values defined in the `kafka_extra_values` variable
will be merged with the ones created with
the `config.yml.j2` template. They will **override**
the default values if defined or values defined
in the other Ansible variable files i.e. they are
of the highest priority.

### Prometheus configuration

These variables configure the Prometheus component:

#### Deployment settings

* `prometheus_image_pull_secrets` - List of image pull
secrets to use for pulling Prometheus images (default: `[]`)
* `prometheus_operator_enabled` - Enable Prometheus
Operator (default: `true`)
* `prometheus_alertmanager_enabled` - Enable Prometheus
 Alertmanager (default: `false`)
* `prometheus_kube_state_metrics_enabled` - Enable
Kube-state-metrics (default: `false`)
* `prometheus_node_exporter_enabled` - Enable
Prometheus Node Exporter (default: `false`)

#### Prometheus agent server settings

* `prometheus_server_replicas` - Number of Prometheus
 server replicas (default: `1`)
* `prometheus_server_memory_request` - Memory request
 for Prometheus server (default: `128Mi`)
* `prometheus_server_memory_limit` - Memory limit for
 Prometheus server (default: `2048Mi`)
* `prometheus_server_cpu_request` - CPU request for
 Prometheus server (default: `100m`)
* `prometheus_server_cpu_limit` - CPU limit for
 Prometheus server (default: `500m`)

* `prometheus_server_remote_write_name` - Name of the
 remote write for Prometheus server (default: name
 of [Kafka adapter] if Kafka is enabled *or* `""` if Kafka is disabled)
* `prometheus_server_remote_write_url` - URL of the
 remote write for Prometheus server (default: recieve
 endpoint of [Kafka adapter] if Kafka is enabled
 *or* `""` if Kafka is disabled)

* `prometheus_server_federation_targets` -
[list of federation scraping targets] i.e.
[additional scrape configs for Helm Chart values] (default: [])

* `prometheus_server_service_account_annotations` -
Annotations for the service account for Prometheus
server (default: `{}`)
* `prometheus_server_extra_args` - Additional arguments
for Prometheus server (default: `{}`)

#### Prometheus configmap reloader settings

* `prometheus_configmap_reloader_memory_request` -
Memory request for Prometheus configmap reloader (default: `10Mi`)
* `prometheus_configmap_reloader_memory_limit` -
Memory limit for Prometheus configmap reloader (default: `50Mi`)
* `prometheus_configmap_reloader_cpu_request` -
CPU request for Prometheus configmap reloader (default: `10m`)
* `prometheus_configmap_reloader_cpu_limit` -
CPU limit for Prometheus configmap reloader (default: `100m`)

#### Prometheus DNS settings

* `prometheus_dns_nameservers` -
List of nameservers for Prometheus (default: `[]`)
* `prometheus_dns_options` -
List of DNS options for Prometheus (default: `[]`)
* `prometheus_dns_searches` -
List of DNS searches for Prometheus (default: `[]`)

#### Prometheus service settings

* `prometheus_service_port` -
Port for Prometheus service (default: `9090`)
* `prometheus_service_annotations` -
Annotations for Prometheus service (default: `{}`)
* `prometheus_service_labels` -
Labels for Prometheus service (default: `{}`)

#### Prometheus ingress settings

* `prometheus_ingress_enabled` -
Enable Prometheus ingress (default: `false`)
* `prometheus_ingress_labels` -
Labels for Prometheus ingress (default: `{}`)
* `prometheus_ingress_hosts` -
List of hosts for Prometheus ingress (default: `[]`)
* `prometheus_ingress_tls_secrets` -
List of TLS secrets for Prometheus ingress (default: `[]`)
* `prometheus_ingress_paths` -
Paths for Prometheus ingress (default: `{}`)

#### Further Prometheus customization

Similar to the Kafka configuration, the Prometheus configuration
can be further customized by passing additional values
to the `prometheus_extra_values` variable. Please refer to the
[Values file present in the Prometheus Helm chart repository]
to check all available options for them (and for their defaults).

### Deep dive into KPA configuration

By design, internal (private) variables that control
the underlying connection between Prometheus, Kafka and
the Kafka adapter are not exposed to the user. However,
they can be changed either by modifying the `config.yml.j2`
template file or underscored variables located
under `roles/<component>/vars/main.yml` files.

## Requirements

* Ansible 2.9+
* Kubernetes cluster

[Kafka adapter]: https://github.com/Telefonica/prometheus-kafka-adapter
[modes of passing extra environment variables]: https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml#L429C1-L436C1
[Values file present in the Kafka Helm chart repository]: https://github.com/bitnami/charts/blob/main/bitnami/kafka/values.yaml
[additional scrape configs for Helm Chart values]: https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml#L3241
[list of federation scraping targets]: https://prometheus.io/docs/prometheus/latest/federation/
[Values file present in the Prometheus Helm chart repository]: https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml
