<script lang="ts">
        // MCP server management UI inspired by LibreChat and LobeHub implementations
        import { onMount, getContext, createEventDispatcher } from 'svelte';
        import { toast } from 'svelte-sonner';
        import { getMCPConnections, setMCPConnections, verifyMCPConnection } from '$lib/apis/configs';

        const i18n = getContext('i18n');
        const dispatch = createEventDispatcher();

        type MCPServer = {
                name: string;
                url: string;
                type: string;
                tools?: string[];
                available_tools?: string[];
        };

        let servers: MCPServer[] = [];

        onMount(async () => {
                try {
                        const res = await getMCPConnections(localStorage.token);
                        servers = res?.MCP_SERVER_CONNECTIONS ?? [];
                } catch (e) {
                        toast.error(`${e}`);
                }
        });

        const addServer = () => {
                servers = [
                        ...servers,
                        { name: '', url: '', type: 'sse', tools: [], available_tools: [] }
                ];
        };

        const removeServer = (idx: number) => {
                servers = servers.filter((_, i) => i !== idx);
        };

        const verify = async (idx: number) => {
                const server = servers[idx];
                try {
                        const res = await verifyMCPConnection(localStorage.token, server);
                        server.available_tools = res.tools || [];
                        server.tools = server.tools || [];
                } catch (e) {
                        toast.error(`${e}`);
                }
        };

        const save = async () => {
                try {
                        await setMCPConnections(localStorage.token, {
                                MCP_SERVER_CONNECTIONS: servers
                        });
                        dispatch('save');
                        toast.success($i18n.t('Settings saved successfully!'));
                } catch (e) {
                        toast.error(`${e}`);
                }
        };
</script>

<div class="flex flex-col gap-3">
        {#each servers as server, idx}
                <div class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg space-y-2">
                        <div class="flex flex-col gap-2 md:flex-row md:gap-2">
                                <input
                                        class="flex-1 px-2 py-1 border rounded"
                                        placeholder="Name"
                                        bind:value={server.name}
                                />
                                <input
                                        class="flex-1 px-2 py-1 border rounded"
                                        placeholder="URL"
                                        bind:value={server.url}
                                />
                                <select class="px-2 py-1 border rounded" bind:value={server.type}>
                                        <option value="sse">SSE</option>
                                        <option value="http">HTTP</option>
                                </select>
                                <button
                                        class="px-2 py-1 text-sm rounded bg-red-500 text-white"
                                        type="button"
                                        on:click={() => removeServer(idx)}
                                >{$i18n.t('Delete')}</button>
                        </div>
                        <div>
                                <button
                                        class="px-2 py-1 text-sm rounded bg-gray-200 dark:bg-gray-800"
                                        type="button"
                                        on:click={() => verify(idx)}
                                >{$i18n.t('Fetch Tools')}</button>
                        </div>
                        {#if server.available_tools && server.available_tools.length > 0}
                                <div class="flex flex-col gap-1 mt-1">
                                        {#each server.available_tools as tool}
                                                <label class="inline-flex items-center gap-1">
                                                        <input
                                                                type="checkbox"
                                                                value={tool}
                                                                bind:group={server.tools}
                                                        />
                                                        <span>{tool}</span>
                                                </label>
                                        {/each}
                                </div>
                        {/if}
                </div>
        {/each}
        <button
                class="px-2 py-1 text-sm rounded bg-gray-200 dark:bg-gray-800"
                type="button"
                on:click={addServer}
        >{$i18n.t('Add')}</button>
</div>

<div class="flex justify-end pt-3 text-sm font-medium">
        <button
                class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
                type="button"
                on:click={save}
        >{$i18n.t('Save')}</button>
</div>
