import { Selection as d3_Selection, BaseType as d3_BaseType } from 'd3-selection';
import { Widget } from '@phosphor/widgets';
export declare class EnvironmentInfoWidget extends Widget {
    d3node: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>;
    static url(trialId: string): string;
    static createItem(parent: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>, key: string, value: string): void;
    static createList(parent: d3_Selection<d3_BaseType, {}, HTMLElement | null, any>, data: {
        [key: string]: string;
    }): void;
    static createNode(trialDisplay: string, data: {
        [key: string]: string;
    }): HTMLElement;
    constructor(trialDisplay: string, data: {
        [key: string]: string;
    });
}
