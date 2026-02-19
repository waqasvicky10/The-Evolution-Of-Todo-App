{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Selector labels for backend
*/}}
{{- define "todo-app.backend.selectorLabels" -}}
app.kubernetes.io/name: todo-backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels for frontend
*/}}
{{- define "todo-app.frontend.selectorLabels" -}}
app.kubernetes.io/name: todo-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
