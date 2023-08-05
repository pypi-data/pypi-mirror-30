import { Selection as d3_Selection, BaseType as d3_BaseType } from 'd3-selection';
import { Widget } from '@phosphor/widgets';
import { FileAccessData } from './structures';
export declare class FileAccessesInfoWidget extends Widget {
    d3node: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>;
    static url(trialId: string): string;
    static createList(parent: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>, data: FileAccessData[]): void;
    static createNode(trialDisplay: string, data: FileAccessData[]): HTMLElement;
    constructor(trialDisplay: string, data: FileAccessData[]);
}
