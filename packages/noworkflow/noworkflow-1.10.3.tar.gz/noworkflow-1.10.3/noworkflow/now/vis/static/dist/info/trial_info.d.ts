import { Selection as d3_Selection, BaseType as d3_BaseType } from 'd3-selection';
import { Widget } from '@phosphor/widgets';
import { VisibleHistoryNode } from '@noworkflow/history';
import { NowVisPanel } from '../nowpanel';
export declare class TrialInfoWidget extends Widget {
    d3node: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>;
    trial: VisibleHistoryNode;
    static createNode(trial: VisibleHistoryNode): HTMLElement;
    constructor(trial: VisibleHistoryNode);
    createFold(parent: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>, title: string, fn: (parentDock: NowVisPanel) => void): void;
    loadModules(): void;
    loadEnvironment(): void;
    loadFileAccess(): void;
}
