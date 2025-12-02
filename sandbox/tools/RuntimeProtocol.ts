import * as net from 'net';
import * as readline from 'readline';

type OutputCategory = 'stdout' | 'stderr' | string;
type RuntimeMessage = {
  type: string;
  action?: string;
  event?: string;
  command?: string;
  data?: any;
  success?: boolean;
};

// Minimal runtime used by the sandbox tools. It mirrors the runtime_protocol.frm
// logic but is authored in TS to avoid Python-specific codegen.
export class RuntimeProtocol {
  private socket: net.Socket | null = null;
  private host = '127.0.0.1';
  private port = 0;
  private exitCode = 0;
  private sequence = 0;
  private lifecycle: 'idle' | 'starting' | 'connecting' | 'connected' | 'running' | 'terminated' = 'idle';
  private breakpoints: Set<number> = new Set();

  async run(): Promise<void> {
    this.lifecycle = 'starting';
    this.exitCode = 0;
    try {
      this.port = this.readConfigPort();
      this.lifecycle = 'connecting';
      await this.connectSocket(this.host, this.port);
      this.lifecycle = 'connected';
      await this.sendHello();
      this.lifecycle = 'running';
      await this.processMessages();
    } catch (error) {
      this.log(`Runtime error: ${error}`);
      await this.sendOutput(`Runtime error: ${error}\n`, 'stderr');
      this.exitCode = 1;
    } finally {
      await this.closeSocket();
      this.lifecycle = 'terminated';
    }
  }

  private readConfigPort(): number {
    const value = process.env['FRAME_DEBUG_PORT'];
    if (!value) {
      throw new Error('FRAME_DEBUG_PORT not set');
    }
    const parsed = parseInt(value, 10);
    if (Number.isNaN(parsed)) {
      throw new Error(`invalid FRAME_DEBUG_PORT value: ${value}`);
    }
    return parsed;
  }

  private async connectSocket(host: string, port: number): Promise<void> {
    this.log(`Connecting to adapter on ${host}:${port}`);
    this.socket = await new Promise<net.Socket>((resolve, reject) => {
      const sock = net.createConnection({ host, port }, () => resolve(sock));
      sock.on('error', reject);
    });
    this.log('Socket connection established');
    await this.sendMessage({ type: 'event', event: 'connected' });
  }

  private async sendHello(): Promise<void> {
    this.log('Sending hello event');
    await this.sendMessage({
      type: 'event',
      event: 'hello',
      data: { message: 'runtime ready' },
    });
  }

  private async processMessages(): Promise<void> {
    if (!this.socket) {
      this.log('Socket not initialized; message processing aborted');
      return;
    }

    const rl = readline.createInterface({ input: this.socket });
    this.log('Event loop started');

    for await (const text of rl) {
      if (!text) continue;

      let message: RuntimeMessage | null = null;
      try {
        message = JSON.parse(text);
      } catch (error) {
        this.log(`Failed to decode message: ${error} (line=${text})`);
        continue;
      }

      const running = await this.handleCommand(message);
      if (!running) {
        rl.close();
        break;
      }
    }
  }

  private async handleCommand(message: RuntimeMessage): Promise<boolean> {
    if (message.type !== 'command') {
      this.log(`Ignoring non-command message: ${JSON.stringify(message)}`);
      return true;
    }

    const action = message.action;
    const payload = message.data || {};
    this.log(`Received command: ${action} payload=${JSON.stringify(payload)}`);

    if (action === 'initialize') {
      await this.sendOutput('TypeScript runtime initialized\n', 'stdout');
      await this.sendMessage({ type: 'event', event: 'ready' });
      if (payload.stopOnEntry) {
        await this.sendMessage({ type: 'event', event: 'stopped', data: { reason: 'entry' } });
      }
    } else if (action === 'ping') {
      this.sequence += 1;
      await this.sendOutput(`TypeScript pong #${this.sequence}\n`, 'stdout');
    } else if (action === 'setBreakpoints') {
      this.breakpoints = new Set(payload.lines || []);
      await this.sendMessage({ type: 'response', command: 'setBreakpoints', success: true });
      await this.sendMessage({ type: 'event', event: 'stopped', data: { reason: 'breakpoint', threadId: 1 } });
    } else if (action === 'continue') {
      await this.sendMessage({ type: 'event', event: 'continued' });
    } else if (action === 'next' || action === 'stepIn' || action === 'stepOut') {
      await this.sendMessage({ type: 'event', event: 'continued' });
      await this.sendMessage({ type: 'event', event: 'stopped', data: { reason: 'step', threadId: 1 } });
    } else if (action === 'pause') {
      await this.sendMessage({ type: 'event', event: 'stopped', data: { reason: 'pause', threadId: 1 } });
    } else if (action === 'raiseException') {
      await this.sendMessage({ type: 'event', event: 'stopped', data: { reason: 'exception', message: 'boom', stack: 'trace', threadId: 1 } });
    } else if (action === 'terminate') {
      const exitCode = payload.exitCode ?? 0;
      this.exitCode = exitCode;
      await this.sendTerminated(exitCode);
      return false;
    } else {
      await this.sendOutput(`Unhandled command: ${action}\n`, 'stderr');
    }

    return true;
  }

  private async sendOutput(output: string, category: OutputCategory): Promise<void> {
    await this.sendMessage({ type: 'event', event: 'output', data: { output, category } });
  }

  private async sendTerminated(code: number): Promise<void> {
    await this.sendMessage({ type: 'event', event: 'terminated', data: { exitCode: code } });
  }

  private async sendMessage(entry: RuntimeMessage): Promise<void> {
    if (!this.socket) {
      this.log(`Dropping message; socket closed: ${JSON.stringify(entry)}`);
      return;
    }

    const serialized = JSON.stringify(entry) + '\n';
    await new Promise<void>((resolve, reject) => {
      this.socket!.write(serialized, 'utf-8', (err?: Error | null) => {
        if (err) reject(err);
        else resolve();
      });
    }).catch((error) => this.log(`Failed to send message: ${error}`));
  }

  private async closeSocket(): Promise<void> {
    if (this.socket) {
      await new Promise<void>((resolve) => {
        this.socket!.end(() => resolve());
        setTimeout(resolve, 50);
      });
    }
    this.socket = null;
  }

  private log(message: string): void {
    console.log(`[runtime] ${message}`);
  }
}
