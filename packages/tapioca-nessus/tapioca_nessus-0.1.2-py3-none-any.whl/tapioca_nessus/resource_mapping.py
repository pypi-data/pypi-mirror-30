# coding: utf-8

RESOURCE_MAPPING = {
    # Agent confg
    'get_agent_config_details': {
        'resource': '/scanners/{scanner_id}/agents/config',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-config/details',
        'methods': ['GET']
    },
    'update_agent_config': {
        'resource': '/scanners/{scanner_id}/agents/config',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-config/edit',
        'methods': ['PUT']
    },

    # Agent Exclusions
    'create_agent_exclusion': {
        'resource': '/scanners/{scanner_id}/agents/exclusions',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-exclusions/create',
        'methods': ['POST']
    },
    'update_agent_exclusion': {
        'resource': '/scanners/{scanner_id}/agents/exclusions/{exclusion_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-exclusions/edit',
        'methods': ['PUT']
    },
    'delete_agent_exclusion': {
        'resource': '/scanners/{scanner_id}/agents/exclusions/{exclusion_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-exclusions/delete',
        'methods': ['DELETE']
    },
    'get_agent_exclusion_details': {
        'resource': '/scanners/{scanner_id}/agents/exclusions/{exclusion_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-exclusions/details',
        'methods': ['GET']
    },
    'get_agent_exclusions': {
        'resource': '/scanners/{scanner_id}/agents/exclusions',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-exclusions/list',
        'methods': ['GET']
    },

    # Agent groups
    'add_agent': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}/agents/{agent_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/add-agent',
        'methods': ['PUT']
    },
    'configure_agent_group': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/configure',
        'methods': ['PUT']
    },
    'create_agent_group': {
        'resource': '/scanners/{scanner_id}/agent-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/create',
        'methods': ['POST']
    },
    'delete_agent_group': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/delete',
        'methods': ['DELETE']
    },
    'delete_agent_from_group': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}/agents/{agent_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/delete-agent',
        'methods': ['DELETE']
    },
    'get_agent_group_details': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/details',
        'methods': ['GET']
    },
    'get_agent_groups': {
        'resource': '/scanners/{scanner_id}/agent-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/agent-groups/list',
        'methods': ['GET']
    },

    # Agents
    'delete_agent': {
        'resource': '/scanners/{scanner_id}/agents/{agent_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agents/delete',
        'methods': ['DELETE']
    },
    'get_agents': {
        'resource': '/scanners/{scanner_id}/agents',
        'docs': 'https://cloud.tenable.com/api#/resources/agents/list',
        'methods': ['DELETE']
    },
    'get_agent': {
        'resource': '/scanners/{scanner_id}/agents/{agent_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/agents/get',
        'methods': ['GET']
    },

    # Assets
    'list_assets': {
        'resource': '/assets',
        'docs': 'https://cloud.tenable.com/api#/resources/assets/list-assets',
        'methods': ['GET']
    },
    'asset_info': {
        'resource': '/assets/{asset_uuid}',
        'docs': 'https://cloud.tenable.com/api#/resources/assets/asset-info',
        'methods': ['GET']
    },
    'import_assets': {
        'resource': '/import/assets',
        'docs': 'https://cloud.tenable.com/api#/resources/assets/import',
        'methods': ['POST']
    },
    'list_import_jobs': {
        'resource': '/import/asset-jobs',
        'docs': 'https://cloud.tenable.com/api#/resources/assets/list-import-jobs',
        'methods': ['GET']
    },
    'get_import_jobs_info': {
        'resource': '/import/asset-jobs/{asset_import_job_uuid}',
        'docs': 'https://cloud.tenable.com/api#/resources/assets/import-job-info',
        'methods': ['GET']
    },

    # Audit log
    'audit_log_events': {
        'resource': '/audit-log/v1/events',
        'docs': 'https://cloud.tenable.com/api#/resources/audit-log/events',
        'methods': ['GET']
    },

    # Bulk operations
    'bulk_add_agent': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}/agents/_bulk/add',
        'docs': 'https://cloud.tenable.com/api#/resources/bulk-operations/bulk-add-agent',
        'methods': ['POST']
    },
    'bulk_remove_agent': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}/agents/_bulk/remove',
        'docs': 'https://cloud.tenable.com/api#/resources/bulk-operations/bulk-remove-agent',
        'methods': ['POST']
    },
    'unlink_agent': {
        'resource': '/scanners/{scanner_id}/agents/_bulk/unlink',
        'docs': 'https://cloud.tenable.com/api#/resources/bulk-operations/bulk-unlink-agent',
        'methods': ['POST']
    },
    'bulk_agent_group_status': {
        'resource': '/scanners/{scanner_id}/agent-groups/{group_id}/agents/_bulk/{task_uuid}',
        'docs': 'https://cloud.tenable.com/api#/resources/bulk-operations/bulk-agent-group-status',
        'methods': ['GET']
    },
    'bulk_agent_status': {
        'resource': '/scanners/{scanner_id}/agents/_bulk/{task_uuid}',
        'docs': 'https://cloud.tenable.com/api#/resources/bulk-operations/bulk-agent-status',
        'methods': ['GET']
    },

    # Editor
    'export_audit_file': {
        'resource': '/editor/{type}/{object_id}/audits/{file_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/editor/audits',
        'methods': ['GET']
    },
    'get_template_details': {
        'resource': '/editor/{type}/templates/{template_uuid}',
        'docs': 'https://cloud.tenable.com/api#/resources/editor/details',
        'methods': ['GET']
    },
    'get_editor_object': {
        'resource': '/editor/{type}/{id}',
        'docs': 'https://cloud.tenable.com/api#/resources/editor/edit',
        'methods': ['GET']
    },
    'get_templates': {
        'resource': '/editor/{type}/templates',
        'docs': 'https://cloud.tenable.com/api#/resources/editor/list',
        'methods': ['GET']
    },
    'get_plugin_description': {
        'resource': '/editor/policy/{policy_id}/families/{family_id}/plugins/{plugin_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/editor/plugin-description',
        'methods': ['GET']
    },

    # Exclusions
    'create_exclusion': {
        'resource': '/exclusions',
        'docs': 'https://cloud.tenable.com/api#/resources/exclusions/create',
        'methods': ['POST']
    },
    'delete_exclusion': {
        'resource': '/exclusions/{list_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/exclusions/delete',
        'methods': ['DELETE']
    },
    'get_exclusion_details': {
        'resource': '/exclusions/{list_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/exclusions/details',
        'methods': ['GET']
    },
    'update_exclusion': {
        'resource': '/exclusions/{list_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/exclusions/edit',
        'methods': ['PUT']
    },
    'get_exclusions': {
        'resource': '/exclusions',
        'docs': 'https://cloud.tenable.com/api#/resources/exclusions/list',
        'methods': ['GET']
    },

    # File
    'file_upload': {
        'resource': '/file/upload',
        'docs': 'https://cloud.tenable.com/api#/resources/file/upload',
        'methods': ['POST']
    },

    # Agents Filters
    'get_agents_filters': {
        'resource': '/filters/scans/agents',
        'docs': 'https://cloud.tenable.com/api#/resources/filters/agents-filters',
        'methods': ['GET']
    },

    # Folders
    'create_folder': {
        'resource': '/folders',
        'docs': 'https://cloud.tenable.com/api#/resources/folders/create',
        'methods': ['POST']
    },
    'delete_folder': {
        'resource': '/folders/{folder_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/folders/delete',
        'methods': ['DELETE']
    },
    'update_folder': {
        'resource': '/folders/{folder_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/folders/edit',
        'methods': ['PUT']
    },
    'get_folders': {
        'resource': '/folders',
        'docs': 'https://cloud.tenable.com/api#/resources/folders/list',
        'methods': ['GET']
    },

    # Groups
    'add_user_to_group': {
        'resource': '/groups/{group_id}/users/{user_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/add-user',
        'methods': ['POST']
    },
    'create_group': {
        'resource': '/groups',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/create',
        'methods': ['POST']
    },
    'delete_group': {
        'resource': '/groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/delete',
        'methods': ['DELETE']
    },
    'delete_user_from_group': {
        'resource': '/groups/{group_id}/users/{user_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/delete-user',
        'methods': ['DELETE']
    },
    'update_group': {
        'resource': '/groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/edit',
        'methods': ['PUT']
    },
    'get_groups': {
        'resource': '/groups',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/list',
        'methods': ['GET']
    },
    'get_users_from_group': {
        'resource': '/groups/{group_id}/users',
        'docs': 'https://cloud.tenable.com/api#/resources/groups/list-users',
        'methods': ['GET']
    },

    # Permissions
    'change_permissions': {
        'resource': '/permissions/{object_type}/{object_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/permissions/change',
        'methods': ['PUT']
    },
    'get_permissions': {
        'resource': '/permissions/{object_type}/{object_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/permissions/list',
        'methods': ['GET']
    },

    # Plugins
    'get_families': {
        'resource': '/plugins/families',
        'docs': 'https://cloud.tenable.com/api#/resources/plugins/families',
        'methods': ['GET']
    },
    'get_family_details': {
        'resource': '/plugins/families/{id}',
        'docs': 'https://cloud.tenable.com/api#/resources/plugins/family-details',
        'methods': ['GET']
    },
    'get_plugin_details': {
        'resource': '/plugins/plugin/{id}',
        'docs': 'https://cloud.tenable.com/api#/resources/plugins/plugin-details',
        'methods': ['GET']
    },

    # Policies
    'configure_policies': {
        'resource': '/policies/{policy_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/configure',
        'methods': ['PUT']
    },
    'copy_policies': {
        'resource': '/policies/{policy_id}/copy',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/copy',
        'methods': ['POST']
    },
    'create_policies': {
        'resource': '/policies',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/create',
        'methods': ['POST']
    },
    'delete_policies': {
        'resource': '/policies/{policy_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/delete',
        'methods': ['DELETE']
    },
    'get_policy': {
        'resource': '/policies/{policy_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/details',
        'methods': ['GET']
    },
    'import_policies': {
        'resource': '/policies/import',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/import',
        'methods': ['POST']
    },
    'export_policies': {
        'resource': '/policies/{policy_id}/export',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/export',
        'methods': ['GET']
    },
    'get_policies': {
        'resource': '/policies',
        'docs': 'https://cloud.tenable.com/api#/resources/policies/list',
        'methods': ['GET']
    },

    # Scanner Group
    'add_scanner_to_group': {
        'resource': '/scanner-groups/{group_id}/scanners/{scanner_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/add-scanner',
        'methods': ['POST']
    },
    'create_scanner_group': {
        'resource': '/scanner-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/create',
        'methods': ['POST']
    },
    'delete_scanner_group': {
        'resource': '/scanner-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/delete',
        'methods': ['DELETE']
    },
    'delete_scanner_from_group': {
        'resource': '/scanner-groups/{group_id}/scanners/{scanner_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/delete-scanner',
        'methods': ['DELETE']
    },
    'get_scanner_group_details': {
        'resource': '/scanner-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/details',
        'methods': ['GET']
    },
    'edit_scanner_group': {
        'resource': '/scanner-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/edit',
        'methods': ['PUT']
    },
    'get_scanner_groups': {
        'resource': '/scanner-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups/list',
        'methods': ['GET']
    },
    'get_scanners_from_group': {
        'resource': '/scanner-groups/{group_id}/scanners',
        'docs': 'https://cloud.tenable.com/api#/resources/scanner-groups',
        'methods': ['GET']
    },

    # Scanners
    'control_scans': {
        'resource': '/scanners/{scanner_id}/scans/{scan_uuid}/control',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/control-scans',
        'methods': ['POST']
    },
    'delete_scanner': {
        'resource': '/scanners/{scanner_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/delete',
        'methods': ['DELETE']
    },
    'get_scanner_details': {
        'resource': '/scanners/{scanner_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/details',
        'methods': ['GET']
    },
    'edit_scan': {
        'resource': '/settings/{scanner_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/edit',
        'methods': ['PUT']
    },
    'get_aws_targets': {
        'resource': '/scanners/{scanner_id}/aws-targets',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/get-aws-targets',
        'methods': ['GET']
    },
    'get_scanner_key': {
        'resource': '/scanners/{scanner_id}/key',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/get-scanner-key',
        'methods': ['GET']
    },
    'get_scanner_scans': {
        'resource': '/scanners/{scanner_id}/scans',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/get-scans',
        'methods': ['GET']
    },
    'list_scanners': {
        'resource': '/scanners',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/list',
        'methods': ['GET']
    },
    'toggle_link_state': {
        'resource': '/settings/{scanner_id}/link',
        'docs': 'https://cloud.tenable.com/api#/resources/scanners/toggle-link-state',
        'methods': ['PUT']
    },

    # Scans
    'get_scan_attachment': {
        'resource': '/scans/{scan_id}/attachments/{attachment_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/attachments',
        'methods': ['GET']
    },
    'configure_scan': {
        'resource': '/scans/{scan_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/configure',
        'methods': ['PUT']
    },
    'copy_scan': {
        'resource': '/scans/{scan_id}/copy',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/copy',
        'methods': ['POST']
    },
    'create_scan': {
        'resource': '/scans',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/create',
        'methods': ['POST']
    },
    'delete_scan': {
        'resource': '/scans/{scan_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/delete',
        'methods': ['DELETE']
    },
    'delete_history_scan': {
        'resource': '/scans/{scan_id}/history/{history_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/delete-history',
        'methods': ['DELETE']
    },
    'get_scan_details': {
        'resource': '/scans/{scan_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/details',
        'methods': ['GET']
    },
    'export_downloand_scan': {
        'resource': '/scans/{scan_id}/export/{file_id}/download',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/export-download',
        'methods': ['GET']
    },
    'export_scan': {
        'resource': '/scans/{scan_id}/export',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/export-request',
        'methods': ['POST']
    },
    'export_status_scan': {
        'resource': '/scans/{scan_id}/export/{file_id}/status',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/export-status',
        'methods': ['GET']
    },
    'get_host_details': {
        'resource': '/scans/{scan_id}/hosts/{host_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/host-details',
        'methods': ['PUT']
    },
    'import_scan': {
        'resource': '/scans/import',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/import',
        'methods': ['POST']
    },
    'launch_scan': {
        'resource': '/scans/{scan_id}/launch',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/launch',
        'methods': ['POST']
    },
    'get_scans': {
        'resource': '/scans',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/list',
        'methods': ['GET']
    },
    'pause_scan': {
        'resource': '/scans/{scan_id}/pause',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/pause',
        'methods': ['POST']
    },
    'get_plugin_output': {
        'resource': '/scans/{scan_id}/hosts/{host_id}/plugins/{plugin_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/plugin-output',
        'methods': ['GET']
    },
    'get_scan_status': {
        'resource': '/scans/{scan_id}/status',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/ready-status',
        'methods': ['GET']
    },
    'get_scan_resume': {
        'resource': '/scans/{scan_id}/resume',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/resume',
        'methods': ['GET']
    },
    'schedule_scan': {
        'resource': '/scans/{scan_id}/schedule',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/schedule',
        'methods': ['PUT']
    },
    'stop_scan': {
        'resource': '/scans/{scan_id}/stop',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/stop',
        'methods': ['POST']
    },
    'get_scans_timezones': {
        'resource': '/scans/timezones',
        'docs': 'https://cloud.tenable.com/api#/resources/scans/timezones',
        'methods': ['GET']
    },

    # Server
    'get_server_properties': {
        'resource': '/server/properties',
        'docs': 'https://cloud.tenable.com/api#/resources/server/properties',
        'methods': ['GET']
    },
    'get_server_status': {
        'resource': '/server/status',
        'docs': 'https://cloud.tenable.com/api#/resources/server/status',
        'methods': ['GET']
    },

    # Session
    'create_session': {
        'resource': '/session',
        'docs': 'https://cloud.tenable.com/api#/resources/session/create',
        'methods': ['POST']
    },
    'destroy_session': {
        'resource': '/session',
        'docs': 'https://cloud.tenable.com/api#/resources/session/destroy',
        'methods': ['DELETE']
    },
    'update_session': {
        'resource': '/session',
        'docs': 'https://cloud.tenable.com/api#/resources/session/edit',
        'methods': ['PUT']
    },
    'get_session': {
        'resource': '/session',
        'docs': 'https://cloud.tenable.com/api#/resources/session/get',
        'methods': ['GET']
    },
    'change_session_password': {
        'resource': '/session/chpasswd',
        'docs': 'https://cloud.tenable.com/api#/resources/session/password',
        'methods': ['PUT']
    },
    'generate_session_keys': {
        'resource': '/session/keys',
        'docs': 'https://cloud.tenable.com/api#/resources/session/keys',
        'methods': ['PUT']
    },
    'two_factor_session': {
        'resource': '/session/two-factor',
        'docs': 'https://cloud.tenable.com/api#/resources/session/two-factor',
        'methods': ['PUT']
    },
    'two_factor_enable_session': {
        'resource': '/session/two-factor/send-verification',
        'docs': 'https://cloud.tenable.com/api#/resources/session/two-factor-enable',
        'methods': ['POST']
    },
    'two_factor_enable_verify_session': {
        'resource': '/session/two-factor/verify-code',
        'docs': 'https://cloud.tenable.com/api#/resources/session/two-factor-enable-verify',
        'methods': ['POST']
    },
    'restore_session': {
        'resource': '/session/restore',
        'docs': 'https://cloud.tenable.com/api#/resources/session/restore',
        'methods': ['POST']
    },

    # Target Groups
    'create_target_group': {
        'resource': '/target-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/target-groups/create',
        'methods': ['POST']
    },
    'delete_target_group': {
        'resource': '/target-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/target-groups/delete',
        'methods': ['DELETE']
    },
    'get_target_group_details': {
        'resource': '/target-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/target-groups/details',
        'methods': ['GET']
    },
    'update_target_group': {
        'resource': '/target-groups/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/target-groups/edit',
        'methods': ['PUT']
    },
    'get_target_groups': {
        'resource': '/target-groups',
        'docs': 'https://cloud.tenable.com/api#/resources/target-groups/list',
        'methods': ['GET']
    },

    # Users
    'create_user': {
        'resource': '/users',
        'docs': 'https://cloud.tenable.com/api#/resources/users/create',
        'methods': ['POST']
    },
    'delete_user': {
        'resource': '/users/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/users/delete',
        'methods': ['DELETE']
    },
    'get_user_details': {
        'resource': '/users/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/users/details',
        'methods': ['GET']
    },
    'update_user': {
        'resource': '/users/{group_id}',
        'docs': 'https://cloud.tenable.com/api#/resources/users/edit',
        'methods': ['PUT']
    },
    'enabled_user': {
        'resource': '/users/{group_id}/enabled',
        'docs': 'https://cloud.tenable.com/api#/resources/users/enabled',
        'methods': ['PUT']
    },
    'two_factor_user': {
        'resource': '/users/{user_id}/two-factor',
        'docs': 'https://cloud.tenable.com/api#/resources/users/two-factor',
        'methods': ['PUT']
    },
    'two_factor_enable_user': {
        'resource': '/users/{user_id}/two-factor/send-verification',
        'docs': 'https://cloud.tenable.com/api#/resources/users/two-factor-enable',
        'methods': ['POST']
    },
    'two_factor_enable_verify_user': {
        'resource': '/users/{user_id}/two-factor/verify-code',
        'docs': 'https://cloud.tenable.com/api#/resources/users/two-factor-enable-verify',
        'methods': ['POST']
    },
    'impersonate_user': {
        'resource': '/users/{user_id}/impersonate',
        'docs': 'https://cloud.tenable.com/api#/resources/users/impersonate',
        'methods': ['POST']
    },
    'get_users': {
        'resource': '/users',
        'docs': 'https://cloud.tenable.com/api#/resources/users/list',
        'methods': ['GET']
    },
    'change_user_password': {
        'resource': '/users/{user_id}/chpasswd',
        'docs': 'https://cloud.tenable.com/api#/resources/users/password',
        'methods': ['PUT']
    },
    'generate_user_keys': {
        'resource': '/users/{user_id}/keys',
        'docs': 'https://cloud.tenable.com/api#/resources/users/keys',
        'methods': ['PUT']
    },

    # Workbench
    'workbenches_vulnerabilities': {
        'resource': '/workbenches/vulnerabilities',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/vulnerabilities',
        'methods': ['GET']
    },
    'workbenches_vulnerabilities_filters': {
        'resource': '/filters/workbenches/vulnerabilities',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/vulnerabilities-filters',
        'methods': ['GET']
    },
    'workbenches_vulnerability_info': {
        'resource': '/workbenches/vulnerabilities/{plugin_id}/info',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/vulnerability-info',
        'methods': ['GET']
    },
    'workbenches_vulnerability_output': {
        'resource': '/workbenches/vulnerabilities/{plugin_id}/outputs',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/vulnerability-output',
        'methods': ['GET']
    },
    'workbenches_assets': {
        'resource': '/workbenches/assets',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/assets',
        'methods': ['GET']
    },
    'workbenches_assets_vulnerabilities': {
        'resource': '/workbenches/assets/vulnerabilities',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/assets-vulnerabilities',
        'methods': ['GET']
    },
    'workbenches_asset_info': {
        'resource': '/workbenches/assets/{asset_id}/info',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/asset-info',
        'methods': ['GET']
    },
    'workbenches_asset_vulnerabilities': {
        'resource': '/workbenches/assets/{asset_id}/vulnerabilities',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/asset-vulnerabilities',
        'methods': ['GET']
    },
    'workbenches_asset_vulnerability_info': {
        'resource': '/workbenches/assets/{asset_id}/vulnerabilities/{plugin_id}/info',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/asset-vulnerability-info',
        'methods': ['GET']
    },
    'workbenches_asset_vulnerability_output': {
        'resource': '/workbenches/assets/{asset_id}/vulnerabilities/{plugin_id}/outputs',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/asset-vulnerability-output',
        'methods': ['GET']
    },
    'workbenches_export_download': {
        'resource': '/workbenches/export/{file_id}/download',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/export-download',
        'methods': ['GET']
    },
    'workbenches_export_request': {
        'resource': '/workbenches/export',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/export-request',
        'methods': ['GET']
    },
    'workbenches_export_status': {
        'resource': '/workbenches/export/{file_id}/status',
        'docs': 'http://cloud.tenable.com/api#/resources/workbenches/export-status',
        'methods': ['GET']
    },
}
