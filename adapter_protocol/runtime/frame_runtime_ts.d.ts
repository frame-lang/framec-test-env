export declare class FrameEvent {
  constructor(message: string, parameters: any[] | null);
  message: string;
  parameters: any[] | null;
}
export declare class FrameCompartment {
  constructor(state: string, enterArgs?: any, exitArgs?: any, stateArgs?: any, stateVars?: any);
  state: string;
  enterArgs?: any;
  exitArgs?: any;
  stateArgs?: any;
  stateVars?: any;
}

// Adapter/runtime helper APIs used by generated TS (declarations for tsc)
declare global {
  function frameRuntimeGetTimestamp(): number;
  function frameRuntimeWait(ms: number): void;

  function frameRuntimeSetDebugAdapter(adapter: any): void;
  function frameRuntimeCreateServer(): { port: number; server: any };
  function frameRuntimeCloseServer(server: any): void;

  function frameRuntimeSetEnv(key: string, value: string): void;
  function frameRuntimeSpawnPython(code: string): { success: boolean; process?: any; pid?: number; error?: string };
  function frameRuntimeKillProcess(proc: any): void;

  function frameRuntimeTranspileFrame(path: string, target: string, debug: boolean): { success: boolean; code: string; sourceMap: any; error?: string };
  function frameRuntimeInjectFrameDebugRuntime(code: string, map: any, port: number): string;

  function frameRuntimeFileExists(path: string): boolean;
  function frameRuntimeGetLength(x: any): number;
  function frameRuntimeGetMapSize(x: any): number;
  function frameRuntimeToString(x: any): string;
  function frameRuntimeStringToNumber(s: string): number;

  function frameRuntimeMapGet(map: any, key: string): any;
  function frameRuntimeMapSet(map: any, key: string, value: any): void;
  function frameRuntimeMapHasKey(map: any, key: string): boolean;
  function frameRuntimeMapKeys(map: any): string[];

  function frameRuntimeSendCommand(server: any, commandType: string, data: any): void;
  function frameRuntimeSendResponse(command: string, body: any): void;
  function frameRuntimeSendEvent(event: string, body: any): void;
}

export {};
