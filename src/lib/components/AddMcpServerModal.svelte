<script lang="ts">
        import { toast } from 'svelte-sonner';
        import { getContext, onMount } from 'svelte';
        const i18n = getContext('i18n');

        import Modal from '$lib/components/common/Modal.svelte';
        import Tags from './common/Tags.svelte';
        import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
        import Spinner from '$lib/components/common/Spinner.svelte';
        import XMark from '$lib/components/icons/XMark.svelte';
        import { verifyMcpServerConnection } from '$lib/apis/configs';

        export let onSubmit: Function = () => {};
        export let onDelete: Function = () => {};

        export let show = false;
        export let edit = false;
        export let connection = null;

        let url = '';
        let type = 'http';
        let key = '';
        let allowed: string[] = [];
        let available: string[] = [];
        let loading = false;

        const verifyHandler = async () => {
                if (url === '') {
                        toast.error($i18n.t('Please enter a valid URL'));
                        return;
                }

                loading = true;
                const res = await verifyMcpServerConnection(localStorage.token, {
                        url,
                        type,
                        key
                }).catch(() => null);
                loading = false;

                if (res) {
                        available = (res.tools || []).map((t) => (t.name ? t.name : t));
                        toast.success($i18n.t('Connection successful'));
                } else {
                        toast.error($i18n.t('Connection failed'));
                }
        };

        const submitHandler = async () => {
                loading = true;
                url = url.replace(/\/$/, '');
                const connection = {
                        url,
                        type,
                        key,
                        allowed_tools: allowed,
                        config: { enable: true }
                };
                await onSubmit(connection);
                loading = false;
                show = false;
                url = '';
                type = 'http';
                key = '';
                allowed = [];
                available = [];
        };

        const init = () => {
                if (connection) {
                        url = connection.url;
                        type = connection.type ?? 'http';
                        key = connection.key ?? '';
                        allowed = connection.allowed_tools ?? [];
                        available = [];
                }
        };

        $: if (show) {
                init();
        }

        onMount(() => {
                init();
        });
</script>

<Modal size="sm" bind:show>
        <div>
                <div class=" flex justify-between dark:text-gray-100 px-5 pt-4 pb-2">
                        <h1 class=" text-lg font-medium self-center font-primary">
                                {#if edit}
                                        {$i18n.t('Edit Connection')}
                                {:else}
                                        {$i18n.t('Add Connection')}
                                {/if}
                        </h1>
                        <button
                                class="self-center"
                                aria-label={$i18n.t('Close Configure Connection Modal')}
                                on:click={() => {
                                        show = false;
                                }}
                        >
                                <XMark className={'size-5'} />
                        </button>
                </div>

                <div class="flex flex-col w-full px-4 pb-4 dark:text-gray-200">
                        <form
                                class="flex flex-col w-full"
                                on:submit={(e) => {
                                        e.preventDefault();
                                        submitHandler();
                                }}
                        >
                                <div class="mb-2">
                                        <label class="text-xs text-gray-500" for="mcp-url">{$i18n.t('URL')}</label>
                                        <input id="mcp-url" class="w-full bg-transparent outline-hidden text-sm" bind:value={url} />
                                </div>
                                <div class="mb-2">
                                        <label class="text-xs text-gray-500" for="mcp-type">{$i18n.t('Type')}</label>
                                        <select id="mcp-type" class="w-full bg-transparent text-sm" bind:value={type}>
                                                <option value="http">HTTP</option>
                                                <option value="sse">SSE</option>
                                        </select>
                                </div>
                                <div class="mb-2">
                                        <label class="text-xs text-gray-500">{$i18n.t('API Key')}</label>
                                        <SensitiveInput inputClassName=" outline-hidden bg-transparent w-full" bind:value={key} required={false} />
                                </div>
                                <div class="mb-2">
                                        <div class="flex justify-between">
                                                <label class="text-xs text-gray-500">{$i18n.t('Allowed Tools')}</label>
                                                {#if available.length > 0}
                                                        <div class="text-xs text-gray-400">{available.join(', ')}</div>
                                                {/if}
                                        </div>
                                        <Tags bind:tags={allowed} />
                                </div>
                                <div class="flex justify-between pt-2">
                                        <button
                                                class="px-3 py-1 text-sm rounded-full bg-gray-200 dark:bg-gray-800"
                                                type="button"
                                                on:click={verifyHandler}
                                        >
                                                {#if loading}
                                                        <Spinner className="size-4" />
                                                {:else}
                                                        {$i18n.t('Verify')}
                                                {/if}
                                        </button>
                                        <div class="space-x-2">
                                                {#if edit}
                                                        <button
                                                                class="px-3 py-1 text-sm rounded-full bg-red-500 text-white"
                                                                type="button"
                                                                on:click={() => {
                                                                        onDelete();
                                                                        show = false;
                                                                }}
                                                        >
                                                                {$i18n.t('Delete')}
                                                        </button>
                                                {/if}
                                                <button
                                                        class="px-3 py-1 text-sm font-medium bg-black text-white rounded-full dark:bg-white dark:text-black"
                                                        type="submit"
                                                >
                                                        {$i18n.t('Save')}
                                                </button>
                                        </div>
                                </div>
                        </form>
                </div>
        </div>
</Modal>
