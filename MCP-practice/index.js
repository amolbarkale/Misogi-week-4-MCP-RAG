import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

async function main() {
  const server = new McpServer({
    name: "my-server",
    version: "1.0.0",
  });

  // Add the tool with proper error handling
  server.tool(
    "add",
    "Add two numbers together",
    {
      a: z.number().describe("First number"),
      b: z.number().describe("Second number")
    },
    async ({ a, b }) => {
      const result = a + b;
      return {
        content: [
          { 
            type: "text", 
            text: `The sum of ${a} and ${b} is ${result}` 
          }
        ]
      };
    }
  );

  // Create transport and connect
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  // Log to stderr so it doesn't interfere with MCP protocol
  console.error("✅ MCP server 'my-server' connected successfully");
}

// Handle errors and cleanup
main().catch(err => {
  console.error("❌ MCP server failed to start:", err);
  process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error("🔄 MCP server shutting down...");
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error("🔄 MCP server shutting down...");
  process.exit(0);
});