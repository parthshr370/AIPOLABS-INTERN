import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

interface EmbeddingSearchResult {
	id: string;
	relevance_score?: number;
	content?: string;
	raw_html?: string;
	max_chunk_similarity?: number;
	avg_chunk_similarity?: number;
	metadata_similarity?: number;
	matching_chunks_count?: number;
	has_metadata_match?: boolean;
	created_at?: string;
	processing_status?: string;
	source?: string;
	asset?: {
		id?: string;
		original_filename?: string;
		source_url?: string;
		storage_bucket?: string;
		storage_path?: string;
	};
}

export class MyMCP extends McpAgent {
	server = new McpServer({
		name: "ContextDB",
		version: "1.0.0",
	});

	async init() {

		// Delete context tool
		this.server.tool("delete_context", { context_id: z.string().describe("The ID of the context to delete"), user_id: z.string().describe("User's authentication session token") }, async ({ context_id, user_id }) => {
			try {
				const base = `${process.env.BACKEND_URL || 'http://127.0.0.1:8000'}`;
				const url = new URL(`${base}/context`);
				url.searchParams.set('context_id', context_id);
				url.searchParams.set('user_id', user_id);

				const response = await fetch(url, {
					method: 'DELETE',
					headers: {
						'Authorization': `Bearer ${user_id}`,
					},
				});

				if (!response.ok) {
					const errorText = await response.text().catch(() => 'Unknown error');
					throw new Error(`Delete failed: ${response.status} ${response.statusText} - ${errorText}`);
				}

				const result = await response.json();
				return {
					content: [{ type: "text", text: `Context ${context_id} deleted successfully` }],
					success: true,
					status: "deleted"
				};
			} catch (error) {
				return {
					content: [{ type: "text", text: `Failed to delete context ${context_id}: ${error instanceof Error ? error.message : String(error)}` }],
					success: false,
					status: "error"
				};
			}
		});

		// Quick search with session authentication
		this.server.tool(
			"context_search",
			{
				query: z.string().describe("The search query to find similar embeddings"),
				user_id: z.string().describe("User's authentication session token"),
			},
			async ({ query, user_id }) => {
				try {
					const base = `${process.env.BACKEND_URL || 'http://127.0.0.1:8000'}`;
					const url = new URL(`${base}/search`);
					url.searchParams.set('query', query);
					url.searchParams.set('user_id', user_id);
					url.searchParams.set('top_k', String(5));
					url.searchParams.set('threshold', String(0.1));

					const response = await fetch(url, {
						method: 'GET',
						headers: {
							'Authorization': `Bearer ${user_id}`,
						},
					});

					if (!response.ok) {
						throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
					}

					const json = await response.json() as { results?: EmbeddingSearchResult[] } | EmbeddingSearchResult[];
					const results = Array.isArray(json) ? json : (json?.results ?? []);
					
					const sanitizeRawHtml = (html: string): string => {
						try {
							let out = html ?? '';
							out = out.replace(/<script[\s\S]*?<\/script>/gi, '')
								.replace(/<style[\s\S]*?<\/style>/gi, '')
								.replace(/<noscript[\s\S]*?<\/noscript>/gi, '')
								.replace(/<!--([\s\S]*?)-->/g, '');
							out = out.replace(/[\t\f\r]+/g, ' ');
							return out.trim();
						} catch {
							return html ?? '';
						}
					};

					const formatted = results.map((result: EmbeddingSearchResult, index: number) => {
						const idShort = result.id?.substring(0, 8) || 'unknown';
						const scorePct = typeof result.relevance_score === 'number' ? `${(result.relevance_score * 100).toFixed(0)}%` : 'N/A';
						const content = result.content ?? 'No content';
						const metaLines = [
							result.asset?.original_filename ? `File: ${result.asset.original_filename}` : undefined,
							result.asset?.source_url ? `Source: ${result.asset.source_url}` : (result.source ? `Source: ${result.source}` : undefined),
							result.created_at ? `Created: ${result.created_at}` : undefined,
							result.processing_status ? `Status: ${result.processing_status}` : undefined,
							typeof result.matching_chunks_count === 'number' ? `Matching chunks: ${result.matching_chunks_count}` : undefined,
						].filter((v): v is string => Boolean(v));

						const raw = (result.raw_html && result.raw_html.trim().length > 0) ? sanitizeRawHtml(result.raw_html) : 'No raw HTML available';

						return [
							`Result ${index + 1} [${idShort}] (Score: ${scorePct})`,
							`Content:`,
							content,
							`Metadata:`,
							...(metaLines.length ? metaLines.map(l => `- ${l}`) : ['- None']),
							`Raw HTML (filtered):`,
							raw,
						].join('\n');
					}).join('\n\n');

					return {
						content: [
							{
								type: "text",
								text: `Quick search found ${results.length} results for: "${query}"\n\n${formatted}`,
							},
						],
					};
				} catch (error) {
					return {
						content: [
							{
								type: "text",
								text: `Error in quick search: ${error instanceof Error ? error.message : String(error)}`,
							},
						],
					};
				}
			},
		);
	}
}

export default {
	fetch(request: Request, env: Env, ctx: ExecutionContext) {
		const url = new URL(request.url);

		if (url.pathname === "/sse" || url.pathname === "/sse/message") {
			return MyMCP.serveSSE("/sse").fetch(request, env, ctx);
		}

		if (url.pathname === "/mcp") {
			return MyMCP.serve("/mcp").fetch(request, env, ctx);
		}

		return new Response("Not found", { status: 404 });
	},
};
