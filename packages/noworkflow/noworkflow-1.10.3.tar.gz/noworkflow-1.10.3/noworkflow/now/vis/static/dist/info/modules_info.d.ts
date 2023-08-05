import { Selection as d3_Selection, BaseType as d3_BaseType } from 'd3-selection';
import { Widget } from '@phosphor/widgets';
import { ModuleData } from './structures';
export declare class ModulesInfoWidget extends Widget {
    d3node: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>;
    static url(trialId: string): string;
    static createList(parent: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>, data: ModuleData[]): void;
    static createNode(trialDisplay: string, data: ModuleData[]): HTMLElement;
    constructor(trialDisplay: string, data: ModuleData[]);
}
